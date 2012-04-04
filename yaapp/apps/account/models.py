from django.conf import settings as yaapp_settings
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.db import models
from django.db.models.aggregates import Count
from django.db.models.signals import post_save, pre_delete
from django.utils.translation import ugettext_lazy as _
from facepy import GraphAPI
from settings import SUBSCRIPTION_NONE, SUBSCRIPTION_PREMIUM
from social_auth.signals import socialauth_not_registered
from sorl.thumbnail import ImageField, get_thumbnail
from tastypie.models import ApiKey, create_api_key
from yabase.models import Radio, RadioUser
import datetime
import json
import logging
import settings as account_settings
import tweepy
import urllib
import yasearch.indexer as yasearch_indexer
import yasearch.search as yasearch_search
import yasearch.utils as yasearch_utils



logger = logging.getLogger("yaapp.account")

class EmailUser(User):
    class Meta:
        proxy = True

    def __unicode__(self):
        return self.email

class UserProfileManager(models.Manager):
    def yasound_friend_count(self):
        return self.all().aggregate(Count('friends'))['friends__count']
    
    def search_user_fuzzy(self, search_text, limit=5):
        users = yasearch_search.search_user(search_text, remove_common_words=True)
        results = []
        if not search_text:
            return results

        for u in users:
            user_info = None
            if u["name"] is not None:
                user_info = u["name"]
            ratio = yasearch_utils.token_set_ratio(search_text.lower(), user_info.lower(), method='mean')
            res = (u, ratio)
            results.append(res)
            
        sorted_results = sorted(results, key=lambda i: i[1], reverse=True)
        return sorted_results[:limit]

class UserProfile(models.Model):
    """
    Store usefule informations about user.
    
    account_type can handle multiple values :
     * single ACCOUNT_TYPE_* values
     * multiple ACCOUNT_MULT_* values
     
    Example of valid account_type:
    
    >> account_type = 'TWITTER'   # only twitter
    >> account_type = 'TW,FB'     # twitter and facebook
    >> account_type = 'FACEBOOK'  # only facebook
    >> account_type = 'FB'        # only facebook
    >> account_type = 'FB,TW,YA'  # facebook, twitter, yasound
    
    Instead of checking the account_type field, you should use the following property:
    
    >> facebook_enabled
    >> twitter_enabled
    >> yasound_enabled
    
    The following methods handle the account_type values:
    
    >> add_account_type()
    >> remove_account_type()
    
    """
    objects = UserProfileManager()
    user = models.OneToOneField(User, verbose_name=_('user'))
    name = models.CharField(max_length = 60, blank=True)
    url = models.URLField(null=True, blank=True)
    account_type = models.CharField(max_length=20, blank=True)
    twitter_uid = models.CharField(max_length=60, null=True, blank=True)
    facebook_uid = models.CharField(max_length=60, null=True, blank=True)
    twitter_token = models.CharField(max_length=256, blank=True)
    twitter_token_secret = models.CharField(max_length=256, blank=True)
    facebook_token = models.CharField(max_length=256, blank=True)
    bio_text = models.TextField(null=True, blank=True)
    picture = ImageField(upload_to=yaapp_settings.PICTURE_FOLDER, null=True, blank=True)
    email_confirmed = models.BooleanField(default=False)
    friends = models.ManyToManyField(User, related_name='friends_profile', null=True, blank=True)
    last_authentication_date = models.DateTimeField(null=True, blank=True)
    
    @property
    def facebook_enabled(self):
        return account_settings.ACCOUNT_TYPE_FACEBOOK in self.account_type or \
            account_settings.ACCOUNT_MULT_FACEBOOK in self.account_type
        
    @property
    def twitter_enabled(self):
        return account_settings.ACCOUNT_TYPE_TWITTER in self.account_type or \
            account_settings.ACCOUNT_MULT_TWITTER in self.account_type

    @property
    def yasound_enabled(self):
        return account_settings.ACCOUNT_TYPE_YASOUND in self.account_type or \
            account_settings.ACCOUNT_MULT_YASOUND in self.account_type
        
    def convert_to_multi_account_type(self, commit=True):
        """
        Convert a single account type to a potential multi account type
        """
        account_type = self.account_type
        if account_type == account_settings.ACCOUNT_TYPE_FACEBOOK:
            account_type = account_settings.ACCOUNT_MULT_FACEBOOK
        elif account_type == account_settings.ACCOUNT_TYPE_TWITTER:
            account_type = account_settings.ACCOUNT_MULT_TWITTER
        elif account_type == account_settings.ACCOUNT_TYPE_YASOUND:
            account_type = account_settings.ACCOUNT_MULT_YASOUND
        if commit:
            self.account_type = account_type
            self.save()
        return account_type
        
    def add_account_type(self, new_account_type, commit=True):
        account_type = self.account_type
        if account_type in account_settings.SINGLE_ACCOUNT_TYPES:
            account_type = self.convert_to_multi_account_type(commit=False)
        
        accounts = []
        if account_type is not None:
            accounts = account_type.split(account_settings.ACCOUNT_TYPE_SEPARATOR)
        if new_account_type not in accounts:
            accounts.append(new_account_type)
        self.account_type = account_settings.ACCOUNT_TYPE_SEPARATOR.join(accounts)
        if commit:
            self.save()
        
    def remove_account_type(self, account_type_to_remove, commit=True):
        account_type = self.account_type
        if account_type in account_settings.SINGLE_ACCOUNT_TYPES:
            account_type = self.convert_to_multi_account_type(commit=False)

        accounts = []
        if account_type is not None:
            accounts = account_type.split(account_settings.ACCOUNT_TYPE_SEPARATOR)
        if account_type_to_remove in accounts:
            accounts.remove(account_type_to_remove)
        self.account_type = account_settings.ACCOUNT_TYPE_SEPARATOR.join(accounts)
        if commit:
            self.save()
    
    def add_facebook_account(self, uid, token):
        try:
            facebook_profile = json.load(urllib.urlopen("https://graph.facebook.com/me?" + urllib.urlencode(dict(access_token=token))))
        except:
            return False
        
        if not facebook_profile:
            return False
        
        if facebook_profile.has_key('error'):
            logger.error(facebook_profile['error'])
            return False
        
        if not facebook_profile.has_key('id'):
            logger.error('no "id" attribute in facebook profile')
            return False
        if facebook_profile['id'] != uid:
            logger.error('uid does not match')
            return False
        
        if UserProfile.objects.filter(facebook_uid=uid).count() > 0:
            logger.error('facebook account already attached to other account')
            return False
        
        self.facebook_uid = uid
        self.facebook_token = token
        self.add_account_type(account_settings.ACCOUNT_MULT_FACEBOOK, commit=False)
        self.save()
            
        try:
            self.scan_friends()
        except:
            pass
        
        try:
            if self.picture is None:
                self.update_with_social_picture()
        except:
            pass
    
        return True
    
    def remove_facebook_account(self):
        if not self.yasound_enabled and not self.twitter_enabled:
            return False
        self.facebook_uid = None
        self.remove_account_type(account_settings.ACCOUNT_MULT_FACEBOOK, commit=False)
        self.facebook_token = ''
        self.facebook_uid = ''
        
        # TODO: refresh friends
        self.save()
        
    def add_twitter_account(self, uid, token, token_secret):
        auth = tweepy.OAuthHandler(yaapp_settings.YASOUND_TWITTER_APP_CONSUMER_KEY, yaapp_settings.YASOUND_TWITTER_APP_CONSUMER_SECRET)
        auth.set_access_token(token, token_secret)
        api = tweepy.API(auth)
        res = api.verify_credentials()
        print res
        if (not res) or (res == False):
            return False
        if res.id != int(uid):
            logger.error('res id does not match for twitter')
        
        if UserProfile.objects.filter(twitter_uid=uid).count() > 0:
            logger.error('twitter account already attached to other account')
            return False
        
        self.twitter_uid = uid
        self.twitter_token = token
        self.twitter_token_secret = token_secret
        self.add_account_type(account_settings.ACCOUNT_MULT_TWITTER, commit=False)
        self.save()

        try:
            self.scan_friends()
        except:
            pass
        
        try:
            if self.picture is None:
                self.update_with_social_picture()
        except:
            pass
    
        return True

    def remove_twitter_account(self):
        if not self.yasound_enabled and not self.facebook_enabled:
            return False
        self.twitter_uid = ''
        self.twitter_token = ''
        self.twitter_token_secret = ''
        self.remove_account_type(account_settings.ACCOUNT_MULT_TWITTER, commit=False)

        # TODO: refresh friends
        self.save()
        
    def add_yasound_account(self, email, password):
        if User.objects.filter(email=email).count() > 0:
            logger.error('yasound account already attached to other account')
            return False
        
        self.user.email = email
        self.user.set_password(password)
        self.user.save()
        self.add_account_type(account_settings.ACCOUNT_MULT_YASOUND, commit=True)
        return True

    def remove_yasound_account(self):
        if not self.twitter_enabled and not self.facebook_enabled:
            return False
        
        self.user.set_password(None)
        self.user.email = ''
        self.user.save()

        self.remove_account_type(account_settings.ACCOUNT_MULT_YASOUND, commit=False)
        
        # TODO: refresh friends
        self.save()
        return True
        
    def __unicode__(self):
        if self.name:
            return self.name
        
        return self.user.username
    
    @property
    def fullname(self):
        if self.name:
            return self.name
        
        return self.user.username
        
    
    @property
    def subscription(self):
        if self.user.username == '846054191@facebook': # mat
            return SUBSCRIPTION_PREMIUM
        if self.user.username == '1060354026@facebook': # meeloo
            return SUBSCRIPTION_PREMIUM
        if self.user.username == '1460646148@facebook': # jerome
            return SUBSCRIPTION_PREMIUM
        if self.user.username == '100001622138259@facebook': # neywen
            return SUBSCRIPTION_PREMIUM
        
        return SUBSCRIPTION_NONE
    
    @property
    def own_radio(self):
        own_radios = Radio.objects.filter(creator=self.user)
        if own_radios.count() == 0:
            return None
        return own_radios[0]        
    
    @property
    def current_radio(self):
        current = self.listened_radio
        if not current:
            current = self.connected_radio
        return current
    
    @property
    def listened_radio(self):
        radio_users = RadioUser.objects.filter(user=self.user, listening=True, radio__ready=True)
        if radio_users.count() == 0:
            return None
        r = radio_users[0].radio
        if not r.is_valid:
            return None
        return r
    
    @property
    def connected_radio(self):
        radio_users = RadioUser.objects.filter(user=self.user, connected=True, radio__ready=True)
        if radio_users.count() == 0:
            return None
        r = radio_users[0].radio
        if not r.is_valid:
            return None
        return r
    
    def fill_user_bundle(self, bundle):
        picture_url = None
        if self.picture:
            try:
                picture_url = get_thumbnail(self.picture, '100x100', crop='center').url
            except:
                pass
        bundle.data['picture'] = picture_url
        bundle.data['bio_text'] = self.bio_text
        bundle.data['name'] = self.name
                   
    def update_with_bundle(self, bundle, created):
        if bundle.data.has_key('bio_text'):
            self.bio_text = bundle.data['bio_text']
        if bundle.data.has_key('facebook_uid'):
            self.facebook_uid = bundle.data['facebook_uid']
        if bundle.data.has_key('twitter_uid'):
            self.twitter_uid = bundle.data['twitter_uid']
        if bundle.data.has_key('facebook_token'):
            self.facebook_token = bundle.data['facebook_token']
        if bundle.data.has_key('twitter_token'):
            self.twitter_token = bundle.data['twitter_token']
        if bundle.data.has_key('name'):
            self.name = bundle.data['name']
            
        if created and bundle.data.has_key('account_type'):
            t = bundle.data['account_type']
            self.account_type = t
            if  t == account_settings.ACCOUNT_TYPE_YASOUND:
                logger.info('new yasound user')
            elif t == account_settings.ACCOUNT_TYPE_FACEBOOK:
                logger.info('new facebook user')
            elif t == account_settings.ACCOUNT_TYPE_TWITTER:
                logger.info('new twitter user')
        self.save()
        
    def scan_friends(self):
        logger.debug('scanning %s' % (unicode(self.id)))
        friend_count = 0
        yasound_friend_count = 0
        if self.facebook_enabled:
            graph = GraphAPI(self.facebook_token)
            
            try:
                friends_response = graph.get('me/friends')
            except GraphAPI.Error:
                logger.error('GraphAPI exception error')
                return friend_count, yasound_friend_count
            if not friends_response.has_key('data'):
                logger.info('No friend data')
                return friend_count, yasound_friend_count
            friends_data = friends_response['data']
            friend_count = len(friends_data)
            logger.debug('found %d facebook friends', friend_count)
            friends_ids = [f['id'] for f in friends_data]
            friends = User.objects.filter(userprofile__facebook_uid__in=friends_ids)
            yasound_friend_count = len(friends)
            logger.debug('among them, %d are registered at yasound', yasound_friend_count)

            self.friends = friends
            self.save()
            for user in friends.all():
                profile = user.userprofile
                profile.friends.add(self.user)
                profile.save()
            
        if self.twitter_enabled:
            auth = tweepy.OAuthHandler(yaapp_settings.YASOUND_TWITTER_APP_CONSUMER_KEY, yaapp_settings.YASOUND_TWITTER_APP_CONSUMER_SECRET)
            auth.set_access_token(self.twitter_token, self.twitter_token_secret)
            api = tweepy.API(auth)
            friends_ids = api.friends_ids()
            friends = User.objects.filter(userprofile__twitter_uid__in=friends_ids)
            self.friends = friends
            self.save()
        return friend_count, yasound_friend_count
            
    def update_with_facebook_picture(self):
        if not self.facebook_enabled:
            return
        graph = GraphAPI(self.facebook_token)
        img = graph.get('me/picture?type=large')
        f = ContentFile(img)
        filename = unicode(datetime.datetime.now()) + '.jpg' # set 'jpg' extension by default (for now, don't know how to know which image format we get)
        self.picture.save(filename, f, save=True)
        radio = Radio.objects.get(creator=self.user)
        radio.picture = self.picture
        radio.save()
        
    def update_with_social_picture(self):
        if self.facebook_enabled:
            self.update_with_facebook_picture()
    
    def update_with_social_data(self):
        self.update_with_social_picture()
        self.scan_friends()
        
    def authenticated(self):
        d = datetime.datetime.now()
        self.last_authentication_date = d
        self.save()
        
    def check_live_status(self):
        MAX_DELAY_BETWEEN_AUTHENTICATIONS = 10 * 60; # 10 minutes
        alive = False
        if self.last_authentication_date:
            since_last_authentication = datetime.datetime.now() - self.last_authentication_date
            total_seconds = since_last_authentication.days * 86400 + since_last_authentication.seconds
            alive = total_seconds <= MAX_DELAY_BETWEEN_AUTHENTICATIONS 
        if not alive:
            RadioUser.objects.filter(user=self.user, connected=True).update(connected=False)
            RadioUser.objects.filter(user=self.user, listening=True).update(listening=False)
        return alive
    
    def build_fuzzy_index(self, upsert=False, insert=True):
        return yasearch_indexer.add_user(self.user, upsert, insert)
    
    def remove_from_fuzzy_index(self):
        return yasearch_indexer.remove_user(self.user)
    
    def save(self, *args, **kwargs):
        update_mongo = False
        if self.pk:
            saved = UserProfile.objects.get(pk=self.pk)
            name_changed = self.name != saved.name
            update_mongo = name_changed
            
        super(UserProfile, self).save(*args, **kwargs)
        if update_mongo:
            self.build_fuzzy_index(upsert=True)
        
    def build_picture_filename(self):
        filename = 'userprofile_%d_picture.png' % self.id
        return filename
        

def create_user_profile(sender, instance, created, **kwargs):  
    if created:  
        profile, created = UserProfile.objects.get_or_create(user=instance)  

def create_radio(sender, instance, created, **kwargs):  
    if created:  
        radio, created = Radio.objects.get_or_create(creator=instance)
        radio.save()

post_save.connect(create_user_profile, sender=User)
post_save.connect(create_api_key, sender=User)
post_save.connect(create_radio, sender=User)

class Device(models.Model):
    """
    Represent a device (iphone, ipad, ..)
    """
    user = models.ForeignKey(User, verbose_name=_('user'))
    uuid = models.CharField(_('uuid'), max_length=255)
    
    class Meta:
        verbose_name = _('device')
        unique_together = ('user', 'uuid')

def user_profile_deleted(sender, instance, created=None, **kwargs):  
    if isinstance(instance, UserProfile):
        user_profile = instance
    else:
        return
    user_profile.remove_from_fuzzy_index()
pre_delete.connect(user_profile_deleted, sender=UserProfile)




