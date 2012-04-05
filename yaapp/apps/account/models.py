from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import post_save, pre_delete
from tastypie.models import create_api_key
from tastypie.models import ApiKey
from yabase.models import Radio, RadioUser
from django.conf import settings as yaapp_settings
import settings as account_settings
import tweepy
from facepy import GraphAPI
import json
import urllib
from settings import SUBSCRIPTION_NONE, SUBSCRIPTION_PREMIUM
import yasearch.indexer as yasearch_indexer
import yasearch.search as yasearch_search
import yasearch.utils as yasearch_utils

from social_auth.signals import socialauth_not_registered
from sorl.thumbnail import ImageField
from sorl.thumbnail import get_thumbnail

from bitfield import BitField

from django.core.files.base import ContentFile
import datetime

from yabase.apns import get_deprecated_devices, send_message

import logging
logger = logging.getLogger("yaapp.account")

YASOUND_NOTIF_PARAMS_ATTRIBUTE_NAME = 'yasound_notif_params'

class UserProfileManager(models.Manager):
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
    objects = UserProfileManager()
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
        default=(2+4+8+16+32+64+128)
    )
    
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
        if self.account_type == account_settings.ACCOUNT_TYPE_YASOUND:
            logger.debug('skipping scan_friends of %s, account = %s' % (unicode(self.id), self.account_type))
            return friend_count, yasound_friend_count
        
        if self.account_type == account_settings.ACCOUNT_TYPE_FACEBOOK:
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
            
        elif self.account_type == account_settings.ACCOUNT_TYPE_TWITTER:
            auth = tweepy.OAuthHandler(yaapp_settings.YASOUND_TWITTER_APP_CONSUMER_KEY, yaapp_settings.YASOUND_TWITTER_APP_CONSUMER_SECRET)
            auth.set_access_token(self.twitter_token, self.twitter_token_secret)
            api = tweepy.API(auth)
            friends_ids = api.friends_ids()
            friends = User.objects.filter(userprofile__twitter_uid__in=friends_ids)
            self.friends = friends
            self.save()
        return friend_count, yasound_friend_count
            
    def update_with_facebook_picture(self):
        if self.account_type != account_settings.ACCOUNT_TYPE_FACEBOOK:
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
        if self.account_type == account_settings.ACCOUNT_TYPE_FACEBOOK:
            self.update_with_facebook_picture()
            
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
        print 'user %s is logged' % self.name
        for f in self.friends.all():
            friend_profile = f.userprofile
            friend_profile.my_friend_is_online(self)
    
    def store_ios_device(self, device_token, token_type):
        device, created = Device.objects.get_or_create(user=self.user, ios_token=device_token, ios_token_type=token_type)
        device.set_registered_now()
        
    def send_APNs_message(self, message, custom_params={}, action_loc_key=None, loc_key=None, loc_args=[]):
        devices = Device.objects.for_userprofile(self)
        for d in devices:
            if d.ios_token and d.ios_token_type:
                sandbox = d.is_sandbox()
                token = d.ios_token
                send_message(token, message, sandbox=sandbox, custom_params=custom_params, action_loc_key=action_loc_key, loc_key=loc_key, loc_args=loc_args)
    
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
        
        #MatTest: following lines commented to test easily
#        if user_profile == self:
#            return
#        if self.connected_radio == radio:
#            return
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
post_save.connect(create_api_key, sender=User)
post_save.connect(create_radio, sender=User)

class DeviceManager(models.Manager):
    def for_user(self, user):
        return self.filter(user=user)
    
    def for_userprofile(self, profile):
        return self.filter(user=profile.user)
    
    def delete_deprecated(self, sandbox=True):
        token_type = account_settings.IOS_TOKEN_TYPE_SANDBOX if sandbox else account_settings.IOS_TOKEN_TYPE_DEVELOPMENT
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
        
    
class Device(models.Model):
    """
    Represent a device (iphone, ipad, ..)
    """
    objects = DeviceManager() 
    user = models.ForeignKey(User, verbose_name=_('user'))
    ios_token = models.CharField(_('ios device token'), max_length=255)
    ios_token_type = models.CharField(max_length=16, choices=account_settings.IOS_TOKEN_TYPE_CHOICES)
    registration_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('device')
        unique_together = ('user', 'ios_token')
        
    def is_sandbox(self):
        return self.ios_token_type == account_settings.IOS_TOKEN_TYPE_SANDBOX
    
    def is_development(self):
        return self.ios_token_type == account_settings.IOS_TOKEN_TYPE_DEVELOPMENT
    
    def set_registered_now(self):
        self.registration_date = datetime.datetime.now()
        self.save()
        
    def save(self, *args, **kwargs):
        creation = (self.pk == None)
        super(Device, self).save(*args, **kwargs)
        if creation:
            Device.objects.filter(ios_token=self.ios_token).exclude(user=self.user).delete() # be sure to 'forget' old registrations for this device
            
    def __unicode__(self):
        return u'%s - %s (%s)' % (self.user.userprofile.name, self.ios_token, self.ios_token_type);

def user_profile_deleted(sender, instance, created=None, **kwargs):  
    if isinstance(instance, UserProfile):
        user_profile = instance
    else:
        return
    user_profile.remove_from_fuzzy_index()
pre_delete.connect(user_profile_deleted, sender=UserProfile)




