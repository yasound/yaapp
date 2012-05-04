from bitfield import BitField
from django.conf import settings as yaapp_settings
from django.contrib.auth import login
from django.contrib.auth.models import User, Group
from django.core.files.base import ContentFile, ContentFile
from django.db import models
from django.db.models.aggregates import Count
from django.db.models.signals import post_save, pre_delete
from django.utils.translation import ugettext_lazy as _, ugettext_lazy as _
from emailconfirmation.models import EmailAddress
from facepy import GraphAPI
from settings import SUBSCRIPTION_NONE, SUBSCRIPTION_PREMIUM
from social_auth.signals import socialauth_not_registered
from sorl.thumbnail import ImageField, get_thumbnail
from tastypie.models import ApiKey, create_api_key
from yabase.apns import get_deprecated_devices, send_message
from yabase.models import Radio, RadioUser
import datetime
import datetime
import json
import logging
import logging
import settings as account_settings
import tweepy
import urllib
import yasearch.indexer as yasearch_indexer
import yasearch.search as yasearch_search
import yasearch.utils as yasearch_utils
import yabase.settings as yabase_settings





logger = logging.getLogger("yaapp.account")

YASOUND_NOTIF_PARAMS_ATTRIBUTE_NAME = 'yasound_notif_params'

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
    twitter_token = models.CharField(max_length=256, blank=True)
    twitter_token_secret = models.CharField(max_length=256, blank=True)
    twitter_username = models.CharField(max_length=30, blank=True)
    twitter_email = models.EmailField(blank=True)

    facebook_uid = models.CharField(max_length=60, null=True, blank=True)
    facebook_token = models.CharField(max_length=256, blank=True)
    facebook_username = models.CharField(max_length=100, blank=True)
    facebook_email = models.EmailField(blank=True)
    facebook_expiration_date = models.CharField(max_length=35, blank=True)

    yasound_email = models.EmailField(blank=True)
    
    bio_text = models.TextField(null=True, blank=True)
    picture = ImageField(upload_to=yaapp_settings.PICTURE_FOLDER, null=True, blank=True)
    email_confirmed = models.BooleanField(default=False)
    friends = models.ManyToManyField(User, related_name='friends_profile', null=True, blank=True)
    last_authentication_date = models.DateTimeField(null=True, blank=True)
    notifications_preferences = BitField(flags=(
        'user_in_radio',
        'friend_in_radio',
        'friend_online',
        'message_posted',
        'song_liked',
        'radio_in_favorites',
        'radio_shared',
        'friend_created_radio'
        ),
        default=(2+8+16+32+64+128)
    ) #default = NO (user_in_radio=1) + YES (friend_in_radio=2) + NO (friend_online=4) + YES (message_posted=8) + YES (song_liked=16) + YES (radio_in_favorites=32) + YES (radio_shared=64) + YES (friend_created_radio=128)
    
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
    
    def add_facebook_account(self, uid, token, username, email, expiration_date):
        try:
            facebook_profile = json.load(urllib.urlopen("https://graph.facebook.com/me?" + urllib.urlencode(dict(access_token=token))))
        except:
            return False, _('Cannot communicate with facebook')
        
        if not facebook_profile:
            return False, _('Cannot get informations from facebook')
        
        if facebook_profile.has_key('error'):
            logger.error(facebook_profile['error'])
            return False, _('Cannot get informations from facebook')
        
        if not facebook_profile.has_key('id'):
            logger.error('no "id" attribute in facebook profile')
            return False, _('Cannot get informations from facebook')
        if facebook_profile['id'] != uid:
            logger.error('uid does not match')
            return False, _('Facebook identification mismatch')
        
        if UserProfile.objects.filter(facebook_uid=uid).exclude(id=self.id).count() > 0:
            logger.error('facebook account already attached to other account')
            return False, _('The Facebook account is already attached to another account.')
        
        self.facebook_uid = uid
        self.facebook_token = token
        self.facebook_username = username
        self.facebook_email = email
        self.facebook_expiration_date = expiration_date
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
    
        return True, _('OK')
    
    def remove_facebook_account(self):
        if (self.yasound_enabled == False) and (self.twitter_enabled == False):
            return False, _('This is the last account, removal is impossible')

        self.facebook_uid = None
        self.remove_account_type(account_settings.ACCOUNT_MULT_FACEBOOK, commit=False)
        self.facebook_token = ''
        self.facebook_uid = ''
        self.facebook_username = ''
        self.facebook_email = ''
        
        # TODO: refresh friends
        self.save()
        return True, _('OK')
        
    def add_twitter_account(self, uid, token, token_secret, username, email):
        auth = tweepy.OAuthHandler(yaapp_settings.YASOUND_TWITTER_APP_CONSUMER_KEY, yaapp_settings.YASOUND_TWITTER_APP_CONSUMER_SECRET)
        auth.set_access_token(token, token_secret)
        api = tweepy.API(auth)
        res = api.verify_credentials()
        print res
        if (not res) or (res == False):
            return False, _('Cannot communicate with Twitter')
        if res.id != int(uid):
            logger.error('res id does not match for twitter')
            return False, _('Twitter account mismatch')
        
        if UserProfile.objects.filter(twitter_uid=uid).exclude(id=self.id).count() > 0:
            logger.error('twitter account already attached to other account')
            return False, _('The twitter account is already attached to another account.')
        
        self.twitter_uid = uid
        self.twitter_token = token
        self.twitter_token_secret = token_secret
        self.twitter_username = username
        self.twitter_email = email
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
    
        return True, _('OK')

    def remove_twitter_account(self):
        if (self.yasound_enabled == False) and (self.facebook_enabled == False):
            return False, _('This is the last account, removal is impossible')
        
        self.twitter_uid = ''
        self.twitter_token = ''
        self.twitter_token_secret = ''
        self.twitter_email = ''
        self.twitter_username = ''
        self.remove_account_type(account_settings.ACCOUNT_MULT_TWITTER, commit=False)

        # TODO: refresh friends
        self.save()
        return True, _('OK')
    
    def add_yasound_account(self, email, password):
        if User.objects.filter(email=email).exclude(id=self.user.id).count() > 0:
            logger.error('yasound account already attached to other account')
            return False, _('An account already exists with this email')
        
        self.user.email = email
        self.user.set_password(password)
        self.user.save()

        self.yasound_email = email
        self.add_account_type(account_settings.ACCOUNT_MULT_YASOUND, commit=False)
        self.save()
        
        EmailAddress.objects.add_email(self.user, email)
        
        return True, _('OK')

    def remove_yasound_account(self):
        if (self.twitter_enabled == False) and (self.facebook_enabled == False):
            return False, _('This is the last account, removal is impossible')
        
        self.user.set_password(None)
        self.user.email = ''
        self.yasound_email = ''
        self.user.save()

        self.remove_account_type(account_settings.ACCOUNT_MULT_YASOUND, commit=False)
        
        # TODO: refresh friends
        self.save()
        
        EmailAddress.objects.filter(user=self.user).delete()
        
        return True, _('OK')
        
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
        try:
            return Radio.objects.filter(creator=self.user)[:1][0]
        except:
            return None
    
    @property
    def current_radio(self):
        current = self.listened_radio
        if not current:
            current = self.connected_radio
        return current
    
    @property
    def listened_radio(self):
        try:
            r =  RadioUser.objects.filter(user=self.user, listening=True, radio__ready=True)[:1][0].radio
            if not r.is_valid:
                return None
            return r
        except:
            return None
    
    @property
    def connected_radio(self):
        try:
            r = RadioUser.objects.filter(user=self.user, connected=True, radio__ready=True)[:1][0].radio
            if not r.is_valid:
                return None
            return r
        except:
            return None
        
    @property
    def picture_url(self):
        if self.picture:
            try:
                url = get_thumbnail(self.picture, '100x100', crop='center').url
            except:
                url = yaapp_settings.DEFAULT_IMAGE
        else:
            url = yaapp_settings.DEFAULT_IMAGE
        return url
    
    def fill_user_bundle(self, bundle):
        bundle.data['picture'] = self.picture_url
        bundle.data['bio_text'] = self.bio_text
        bundle.data['name'] = self.name
        
    def fill_user_bundle_with_login_infos(self, bundle):
        if self.user:
            bundle.data['username'] = self.user.username
        
        if self.facebook_uid:
            bundle.data['facebook_uid'] = self.facebook_uid
            
        if self.facebook_email:
            bundle.data['facebook_email'] = self.facebook_email

        if self.facebook_username:
            bundle.data['facebook_username'] = self.facebook_username
            
        if self.facebook_token:
            bundle.data['facebook_token'] = self.facebook_token

        if self.facebook_expiration_date:
            bundle.data['facebook_expiration_date'] = self.facebook_expiration_date

        if self.twitter_uid:
            bundle.data['twitter_uid'] = self.twitter_uid
            
        if self.twitter_token:
            bundle.data['twitter_token'] = self.twitter_token
            
        if self.twitter_token_secret:
            bundle.data['twitter_token_secret'] = self.twitter_token_secret
        
        if self.twitter_email:
            bundle.data['twitter_email'] = self.twitter_email

        if self.twitter_username:
            bundle.data['twitter_username'] = self.twitter_username
            
        if self.yasound_email:
            bundle.data['yasound_email'] = self.yasound_email
        
        if bundle.request and hasattr(bundle.request, 'app_id'):
            app_id = bundle.request.app_id
            if app_id == yabase_settings.IPHONE_TECH_TOUR_APPLICATION_IDENTIFIER:
                self.add_to_group(yabase_settings.TECH_TOUR_GROUP_NAME)
           
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
            except GraphAPI.FacebookError:
                logger.error('GraphAPI exception error')
                return friend_count, yasound_friend_count
            except GraphAPI.HTTPError:
                logger.error('GraphAPI exception error (http)')
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
            
        if self.twitter_enabled:
            auth = tweepy.OAuthHandler(yaapp_settings.YASOUND_TWITTER_APP_CONSUMER_KEY, yaapp_settings.YASOUND_TWITTER_APP_CONSUMER_SECRET)
            auth.set_access_token(self.twitter_token, self.twitter_token_secret)
            api = tweepy.API(auth)
            friends_ids = api.friends_ids()
            friends = User.objects.filter(userprofile__twitter_uid__in=friends_ids)
            for friend in friends:
                self.friends.add(friend)
            self.save()

        for user in self.friends.all():
            profile = user.userprofile
            if profile is None:
                continue
            profile.friends.add(self.user)
            profile.save()
            
        return friend_count, yasound_friend_count
            
    def update_with_facebook_picture(self):
        if not self.facebook_enabled:
            return
        graph = GraphAPI(self.facebook_token)
        img = graph.get('me/picture?type=large')
        f = ContentFile(img)
        self.set_picture(f)
        radios = Radio.objects.filter(creator=self.user)
        for r in radios:
            r.set_picture(f)
        
    def update_with_social_picture(self):
        if self.facebook_enabled:
            self.update_with_facebook_picture()
    
    def update_with_social_data(self):
        self.update_with_social_picture()
        self.scan_friends()
        
    def set_picture(self, data):
        filename = self.build_picture_filename()
        if self.picture and len(self.picture.name) > 0:
            self.picture.delete(save=True)
        self.picture.save(filename, data, save=True)
        
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
    
    def radio_is_ready(self, radio):
        for f in self.friends.all():
            friend_profile = f.userprofile
            friend_profile.my_friend_created_radio(friend_profile, radio)
            
    def logged(self):
        for f in self.friends.all():
            try:
                friend_profile = f.userprofile
                friend_profile.my_friend_is_online(self)
            except:
                pass
    
    def add_to_group(self, group_name):
        g, _created = Group.objects.get_or_create(name=group_name)
        g.user_set.add(self.user)
        
    def send_APNs_message(self, message, custom_params={}, action_loc_key=None, loc_key=None, loc_args=[]):
        devices = Device.objects.for_userprofile(self)
        for d in devices:
            if d.ios_token and d.ios_token_type:
                sandbox = d.is_sandbox()
                token = d.ios_token
                app_id = d.application_identifier
                send_message(token, message, sandbox=sandbox, application_id=app_id, custom_params=custom_params, action_loc_key=action_loc_key, loc_key=loc_key, loc_args=loc_args)
    
    def user_in_my_radio(self, user_profile, radio):
        if user_profile.user in self.friends.all():
            self._friend_in_my_radio_internal(user_profile, radio)
        else:
            self._user_in_my_radio_internal(user_profile, radio)
            
    def _friend_in_my_radio_internal(self, friend_profile, radio):
        if not self.notifications_preferences.friend_in_radio:
            return
        if friend_profile == self:
            return
        if self.connected_radio == radio:
            return
        custom_params = {}
        custom_params['user_id'] = friend_profile.user.id
        custom_params['radio_id'] = radio.id
        self.send_APNs_message(message=None, custom_params={YASOUND_NOTIF_PARAMS_ATTRIBUTE_NAME:custom_params}, loc_key='APNs_FIR', loc_args=[friend_profile.name])

    def _user_in_my_radio_internal(self, user_profile, radio):
        if not self.notifications_preferences.user_in_radio:
            return
        if user_profile == self:
            return
        if self.connected_radio == radio:
            return
        custom_params = {}
        custom_params['user_id'] = user_profile.user.id
        custom_params['radio_id'] = radio.id
        self.send_APNs_message(message=None, custom_params={YASOUND_NOTIF_PARAMS_ATTRIBUTE_NAME:custom_params}, loc_key='APNs_UIR', loc_args=[user_profile.name])
        
        
    def my_friend_is_online(self, friend_profile):
        if not self.notifications_preferences.friend_online:
            return
        if friend_profile == self:
            return
        custom_params = {}
        custom_params['user_id'] = friend_profile.user.id
        self.send_APNs_message(message=None, custom_params={YASOUND_NOTIF_PARAMS_ATTRIBUTE_NAME:custom_params}, loc_key='APNs_FOn', loc_args=[friend_profile.name])
        
    def message_posted_in_my_radio(self, wall_message):
        if not self.notifications_preferences.message_posted:
            return
        user_profile = wall_message.user.userprofile
        radio = wall_message.radio
        
        if user_profile == self:
            return
        if self.connected_radio == radio:
            return
        custom_params = {}
        custom_params['uID'] = user_profile.user.id
        custom_params['rID'] = radio.id
        self.send_APNs_message(message=None, custom_params={YASOUND_NOTIF_PARAMS_ATTRIBUTE_NAME:custom_params}, loc_key="APNs_Msg", loc_args=[user_profile.name])
        
    def song_liked_in_my_radio(self, user_profile, radio, song):
        if not self.notifications_preferences.song_liked:
            return
        if user_profile == self:
            return
        if self.connected_radio == radio:
            return
        custom_params = {}
        custom_params['uID'] = user_profile.user.id
        custom_params['rID'] = radio.id
        custom_params['sID'] = song.id
        self.send_APNs_message(message=None, custom_params={YASOUND_NOTIF_PARAMS_ATTRIBUTE_NAME:custom_params}, loc_key='APNs_Sng', loc_args=[user_profile.name, song.metadata.name])
        
    def my_radio_added_in_favorites(self, user_profile, radio):
        if not self.notifications_preferences.radio_in_favorites:
            return
        if user_profile == self:
            return
        custom_params = {}
        custom_params['uID'] = user_profile.user.id
        custom_params['rID'] = radio.id
        self.send_APNs_message(message=None, custom_params={YASOUND_NOTIF_PARAMS_ATTRIBUTE_NAME:custom_params}, loc_key='APNs_RIF', loc_args=[user_profile.name])
        
    def my_radio_shared(self, user_profile, radio):
        if not self.notifications_preferences.radio_shared:
            return
        if user_profile == self:
            return
        custom_params = {}
        custom_params['uID'] = user_profile.user.id
        custom_params['rID'] = radio.id
        self.send_APNs_message(message=None, custom_params={YASOUND_NOTIF_PARAMS_ATTRIBUTE_NAME:custom_params}, loc_key='APNs_RSh', loc_args=[user_profile.name])
        
    def my_friend_created_radio(self, friend_profile, radio):
        if not self.notifications_preferences.friend_created_radio:
            return
        custom_params = {}
        custom_params['uID'] = friend_profile.user.id
        custom_params['rID'] = radio.id
        self.send_APNs_message(message=None, custom_params={YASOUND_NOTIF_PARAMS_ATTRIBUTE_NAME:custom_params}, loc_key='APNs_FCR', loc_args=[friend_profile.name])
        
    def message_from_yasound(self, url_param):
        custom_params = {}
        custom_params['url'] = url_param
        self.send_APNs_message(message=None, custom_params={YASOUND_NOTIF_PARAMS_ATTRIBUTE_NAME:custom_params}, loc_key='APNs_YAS')
        
        
    def notif_preferences(self):
        prefs = {}
        prefs['user_in_radio'] = True if self.notifications_preferences.user_in_radio else False
        prefs['friend_in_radio'] = True if self.notifications_preferences.friend_in_radio else False
        prefs['friend_online'] = True if self.notifications_preferences.friend_online else False
        prefs['message_posted'] = True if self.notifications_preferences.message_posted else False
        prefs['song_liked'] = True if self.notifications_preferences.song_liked else False
        prefs['radio_in_favorites'] = True if self.notifications_preferences.radio_in_favorites else False
        prefs['radio_shared'] = True if self.notifications_preferences.radio_shared else False
        prefs['friend_created_radio'] = True if self.notifications_preferences.friend_created_radio else False
        return prefs
    
    def set_notif_preferences(self, pref_dict):
        user_in_radio = pref_dict.get('user_in_radio', None)
        friend_in_radio = pref_dict.get('friend_in_radio', None)
        friend_online = pref_dict.get('friend_online', None)
        message_posted = pref_dict.get('message_posted', None)
        song_liked = pref_dict.get('song_liked', None)
        radio_in_favorites = pref_dict.get('radio_in_favorites', None)
        radio_shared = pref_dict.get('radio_shared', None)
        friend_created_radio = pref_dict.get('friend_created_radio', None)
        
        if user_in_radio != None:
            self.notifications_preferences.user_in_radio = user_in_radio
        if friend_in_radio != None:
            self.notifications_preferences.friend_in_radio = friend_in_radio
        if friend_online != None:
            self.notifications_preferences.friend_online = friend_online
        if message_posted != None:
            self.notifications_preferences.message_posted = message_posted
        if song_liked != None:
            self.notifications_preferences.song_liked = song_liked
        if radio_in_favorites != None:
            self.notifications_preferences.radio_in_favorites = radio_in_favorites
        if radio_shared != None:
            self.notifications_preferences.radio_shared = radio_shared
        if friend_created_radio != None:
            self.notifications_preferences.friend_created_radio = friend_created_radio 
        self.save()
        
        
        

def create_user_profile(sender, instance, created, **kwargs):  
    if created:  
        profile, created = UserProfile.objects.get_or_create(user=instance)  

def create_radio(sender, instance, created, **kwargs):  
    if created:  
        radio, created = Radio.objects.get_or_create(creator=instance)
        radio.save()

post_save.connect(create_user_profile, sender=User)
post_save.connect(create_user_profile, sender=EmailUser)
post_save.connect(create_api_key, sender=User)
post_save.connect(create_api_key, sender=EmailUser)
post_save.connect(create_radio, sender=User)
post_save.connect(create_radio, sender=EmailUser)

def get_techtour_group():
    g, created = Group.objects.get_or_create(name=yabase_settings.TECH_TOUR_GROUP_NAME)
    return g

class DeviceManager(models.Manager):
    def for_user(self, user):
        return self.filter(user=user)
    
    def for_userprofile(self, profile):
        return self.filter(user=profile.user)
    
    def delete_deprecated(self, sandbox=True):
        token_type = account_settings.IOS_TOKEN_TYPE_SANDBOX if sandbox else account_settings.IOS_TOKEN_TYPE_PRODUCTION
        apns_deprecated = get_deprecated_devices(sandbox)
        for i in apns_deprecated:
            feedback_time = i[0]
            device_token = i[1]
            try:
                device = self.get(ios_token=device_token, ios_token_type=token_type)
                if device.registration_date < feedback_time:
                    device.delete()
            except:
                pass
            
    def store_ios_token(self, user, device_uuid, device_token_type, device_token, app_identifier):
        if app_identifier is None:
            app_identifier = yabase_settings.IPHONE_DEFAULT_APPLICATION_IDENTIFIER
        device, _created = self.get_or_create(user=user, uuid=device_uuid, ios_token_type=device_token_type, application_identifier=app_identifier)
        device.ios_token = device_token
        device.save()
        device.set_registered_now()
        
    
class Device(models.Model):
    """
    Represent a device (iphone, ipad, ..)
    """
    objects = DeviceManager() 
    user = models.ForeignKey(User, verbose_name=_('user'))
    uuid = models.CharField(_('ios device uuid'), max_length=255)
    ios_token = models.CharField(_('ios device token'), max_length=255)
    ios_token_type = models.CharField(max_length=16, choices=account_settings.IOS_TOKEN_TYPE_CHOICES)
    registration_date = models.DateTimeField(auto_now_add=True)
    application_identifier = models.CharField(_('ios application identifier'), max_length=127, default=yabase_settings.IPHONE_DEFAULT_APPLICATION_IDENTIFIER)
    
    class Meta:
        verbose_name = _('device')
        unique_together = ('user', 'ios_token')
        
    def is_sandbox(self):
        return self.ios_token_type == account_settings.IOS_TOKEN_TYPE_SANDBOX
    
    def is_production(self):
        return self.ios_token_type == account_settings.IOS_TOKEN_TYPE_PRODUCTION
    
    def set_registered_now(self):
        self.registration_date = datetime.datetime.now()
        self.save()
        
    def save(self, *args, **kwargs):
        creation = (self.pk == None)
        token_just_set = creation
        if not creation:
            old_token = Device.objects.get(pk=self.pk).ios_token
            token_just_set = old_token != self.ios_token
        super(Device, self).save(*args, **kwargs)
        if token_just_set:
            Device.objects.filter(ios_token=self.ios_token, application_identifier=self.application_identifier).exclude(user=self.user).delete() # be sure to 'forget' old registrations for this device
            
    def __unicode__(self):
        return u'%s - %s - %s (%s)' % (self.user.userprofile.name, self.application_identifier, self.ios_token, self.ios_token_type);
    

def user_profile_deleted(sender, instance, created=None, **kwargs):  
    if isinstance(instance, UserProfile):
        user_profile = instance
    else:
        return
    user_profile.remove_from_fuzzy_index()
pre_delete.connect(user_profile_deleted, sender=UserProfile)




