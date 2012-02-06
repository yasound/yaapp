from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import post_save
from tastypie.models import create_api_key
from tastypie.models import ApiKey
from yabase.models import Radio, RadioUser
from django.conf import settings as yaapp_settings
import settings as account_settings
import tweepy
from facepy import GraphAPI
import json
import urllib
import uuid
from settings import SUBSCRIPTION_NONE, SUBSCRIPTION_PREMIUM
from django.core.files.base import ContentFile
import datetime

class UserProfile(models.Model):
    user = models.OneToOneField(User, verbose_name=_('user'))
    name = models.CharField(max_length = 60, blank=True)
    url = models.URLField(null=True, blank=True)
    account_type = models.CharField(max_length=20, default=account_settings.ACCOUNT_TYPE_YASOUND)
    twitter_uid = models.CharField(max_length=60, null=True, blank=True)
    facebook_uid = models.CharField(max_length=60, null=True, blank=True)
    twitter_token = models.CharField(max_length=256, blank=True)
    twitter_token_secret = models.CharField(max_length=256, blank=True)
    facebook_token = models.CharField(max_length=256, blank=True)
    bio_text = models.TextField(null=True, blank=True)
    picture = models.ImageField(upload_to=yaapp_settings.PICTURE_FOLDER, null=True, blank=True)
    email_confirmed = models.BooleanField(default=False)
    friends = models.ManyToManyField(User, related_name='friends_profile', null=True, blank=True)
    
    def __unicode__(self):
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
            picture_url = self.picture.url
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
                print 'new yasound user'
            elif t == account_settings.ACCOUNT_TYPE_FACEBOOK:
                print 'new facebook user'
            elif t == account_settings.ACCOUNT_TYPE_TWITTER:
                print 'new twitter user'
        self.save()
        
    def scan_friends(self):
        if self.account_type == account_settings.ACCOUNT_TYPE_YASOUND:
            print 'cannot retrieve friends from yasound account'
            return
        
        if self.account_type == account_settings.ACCOUNT_TYPE_FACEBOOK:
            # FIXME: facebook token seems to expire!!!
            print 'scan facebook friends'
            graph = GraphAPI(self.facebook_token)
            friends_response = graph.get('me/friends')
            if not friends_response.has_key('data'):
                print 'no friend data'
                return
            friends_data = friends_response['data']
            friends_ids = []
            for f in friends_data:
                friends_ids.append(f['id'])
            friends = User.objects.filter(userprofile__facebook_uid__in=friends_ids)
            print 'friends:'
            print friends
            self.friends = friends
            self.save()
            
        elif self.account_type == account_settings.ACCOUNT_TYPE_TWITTER:
            auth = tweepy.OAuthHandler(yaapp_settings.YASOUND_TWITTER_APP_CONSUMER_KEY, yaapp_settings.YASOUND_TWITTER_APP_CONSUMER_SECRET)
            auth.set_access_token(self.twitter_token, self.twitter_token_secret)
            api = tweepy.API(auth)
            friends_ids = api.friends_ids()
            friends = User.objects.filter(userprofile__twitter_uid__in=friends_ids)
            self.friends = friends
            self.save()
            
    def update_with_facebook_picture(self):
        if self.account_type != account_settings.ACCOUNT_TYPE_FACEBOOK:
            return
        graph = GraphAPI(self.facebook_token)
        img = graph.get('me/picture?type=square')
        f = ContentFile(img)
        filename = unicode(datetime.datetime.now()) + '.jpg' # set 'jpg' extension by default (for now, don't know how to know which image format we get)
        self.picture.save(filename, f, save=True)
        radio = Radio.objects.get(creator=self.user)
        radio.picture = self.picture
        radio.save()
        
    def update_with_social_picture(self):
        if self.account_type == account_settings.ACCOUNT_TYPE_FACEBOOK:
            self.update_with_facebook_picture()
        

def create_user_profile(sender, instance, created, **kwargs):  
    if created:  
        profile, created = UserProfile.objects.get_or_create(user=instance)  

def create_radio(sender, instance, created, **kwargs):  
    if created:  
        radio, created = Radio.objects.get_or_create(creator=instance)
        radio.uuid = uuid.uuid4().hex
        radio.save()

post_save.connect(create_user_profile, sender=User)
post_save.connect(create_api_key, sender=User)
post_save.connect(create_radio, sender=User)









