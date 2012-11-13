from account.task import async_tw_post_message, async_tw_like_song, \
    async_tw_listen, async_tw_animator_activity
from bitfield import BitField
from django.conf import settings, settings as yaapp_settings
from django.contrib.auth.models import User, Group
from django.core.files.base import ContentFile
from django.db import models
from django.db.models.aggregates import Count
from django.db.models.signals import post_save, pre_delete
from django.utils.translation import ugettext_lazy as _
from emailconfirmation.models import EmailAddress
from facepy import GraphAPI
from settings import SUBSCRIPTION_NONE, SUBSCRIPTION_PREMIUM
from social_auth.signals import socialauth_registered
from social_auth.models import UserSocialAuth
from sorl.thumbnail import ImageField, get_thumbnail, delete
from tastypie.models import create_api_key
from yabase import signals as yabase_signals
from yabase.apns import get_deprecated_devices, send_message
from yabase.models import Radio, RadioUser
from yahistory.models import UserHistory
from yamessage.models import NotificationsManager
import datetime
import json
import logging
import math
import settings as account_settings
import signals as account_signals
import tweepy
import urllib
import yabase.settings as yabase_settings
import yamessage.settings as yamessage_settings
import yasearch.indexer as yasearch_indexer
import yasearch.search as yasearch_search
import yasearch.utils as yasearch_utils
from yacore.geoip import request_country
from yageoperm import utils as yageoperm_utils
import requests
from pymongo import DESCENDING
from dateutil.relativedelta import *
from django.contrib.auth import signals as auth_signals

logger = logging.getLogger("yaapp.account")

YASOUND_NOTIF_PARAMS_ATTRIBUTE_NAME = 'yasound_notif_params'

def latitude_longitude_to_coords(lat, lon, unit='degrees'):
    if lat is None or lon is None:
        return (None, None, None)
    if unit == 'degrees':
        lat = math.radians(lat)
        lon = math.radians(lon)

    x = math.cos(lat) * math.cos(lon)
    y = math.cos(lat) * math.sin(lon)
    z = math.sin(lat)
    return (x, y, z)



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

    def popular_users(self):
        return User.objects.filter(is_active=True)

    def broadcast_message_from_yasound(self, url):
        for p in UserProfile.objects.all():
            p.message_from_yasound(url_param=url)

    def create_fake_users(self, count=10):
        lat_count = math.sqrt(count)
        lon_count = math.ceil(float(count) / float(lat_count))
        lat_min = -90
        lat_range = 180
        lon_min = -180
        lon_range = 360

        lat_inc = lat_range / lat_count
        lon_inc = lon_range / lon_count

        for i in range(count):
            lat = lat_min + lat_inc * (i % lat_count)
            lon = lon_min + lon_inc * math.floor(i / lat_count)
            u = User.objects.create(username='_____fake_____%d' % i)
            p = u.get_profile()
            p.set_position(lat, lon)

    def remove_fake_users(self):
        User.objects.filter(username__startswith='_____fake_____').delete()

    def connected_userprofiles(self, ref_lat, ref_lon, skip=0, limit=20, exclude_profile=None, formula_type='chord', time_condition_enabled=True):
        if ref_lat is None or ref_lon is None:
            return None
        dist_field_name = 'distance'

        if formula_type == 'arc':
            a = 'POWER(SIN(0.5 * (%f - latitude) / 180.0 * PI()), 2) + %f * COS(latitude / 180.0 * PI()) * POWER(SIN(0.5 * (%f - longitude) / 180.0 * PI()), 2)' % (ref_lat, math.cos(math.radians(ref_lat)), ref_lon)
            formula = '%d * ATAN2(SQRT(%s), SQRT(1 - (%s)))' % (3856 * 2, a, a)
        elif formula_type == 'chord':
            ref_coords = latitude_longitude_to_coords(ref_lat, ref_lon, 'degrees')
            if ref_coords[0] is None or ref_coords[1] is None or ref_coords[2] is None:
                return None
            formula_params = {'ref_x': ref_coords[0],
                              'ref_y': ref_coords[1],
                              'ref_z': ref_coords[2]
                              }
            formula = '(x_coord - %(ref_x)f) * (x_coord - %(ref_x)f) + (y_coord - %(ref_y)f) * (y_coord - %(ref_y)f) + (z_coord - %(ref_z)f) * (z_coord - %(ref_z)f)' % formula_params
        else:
            return None

        id_condition = 'id <> %d AND' % exclude_profile.id if exclude_profile is not None else ''
        lat_condition = 'latitude IS NOT NULL AND'
        lon_condition = 'longitude IS NOT NULL AND'
        time_condition = 'last_authentication_date >= DATE_SUB(NOW(), INTERVAL 10 MINUTE)' if time_condition_enabled else ''

        order_info = 'ORDER BY %s ASC' % dist_field_name
        skip_info = ('OFFSET %d' % skip) if (skip is not None and skip > 0) else ''
        limit_info = ('LIMIT %d' % limit) if (limit is not None) else ''

        format_params = {'formula': formula,
                         'dist_field_name': dist_field_name,
                         'id_cond': id_condition,
                         'lat_cond': lat_condition,
                         'lon_cond': lon_condition,
                         'time_cond': time_condition,
                         'order': order_info,
                         'skip': skip_info,
                         'limit': limit_info
                         }
        query = 'SELECT id, %(formula)s as %(dist_field_name)s FROM account_userprofile WHERE %(id_cond)s %(lat_cond)s %(lon_cond)s %(time_cond)s %(order)s %(skip)s %(limit)s' % format_params
        raw = UserProfile.objects.raw(query)
        profiles = list(raw)
        return profiles

class UserProfile(models.Model):
    """Store useful informations about user.

    account_type can handle multiple values :
     * single ACCOUNT_TYPE_* values
     * multiple ACCOUNT_MULT_* values

    Example of valid account_type::

        > user_profile.account_type = 'TWITTER'   # only twitter
        > user_profile.account_type = 'TW,FB'     # twitter and facebook
        > user_profile.account_type = 'FACEBOOK'  # only facebook
        > user_profile.account_type = 'FB'        # only facebook
        > user_profile.account_type = 'FB,TW,YA'  # facebook, twitter, yasound

    Instead of checking the account_type field, you should use the following property::

        > user_profile.facebook_enabled
        > user_profile.twitter_enabled
        > user_profile.yasound_enabled

    The following methods handle the account_type values::

        > user_profile.add_account_type()
        > user_profile.remove_account_type()

    """

    objects = UserProfileManager()
    user = models.OneToOneField(User, verbose_name=_('user'))
    name = models.CharField(_('name'), max_length = 60, blank=True)
    url = models.URLField(_('web site'), null=True, blank=True)

    account_type = models.CharField(_('account type'), max_length=20, blank=True)
    twitter_uid = models.CharField(_('twitter uid'), max_length=60, null=True, blank=True)
    twitter_token = models.CharField(_('twitter token'), max_length=256, blank=True)
    twitter_token_secret = models.CharField(_('twitter token secret'), max_length=256, blank=True)
    twitter_username = models.CharField(_('twitter username'), max_length=30, blank=True)
    twitter_email = models.EmailField(_('twitter email'), blank=True)

    facebook_uid = models.CharField(_('facebook uid'), max_length=60, null=True, blank=True)
    facebook_token = models.CharField(_('facebook token'),max_length=256, blank=True)
    facebook_username = models.CharField(_('facebook username'),max_length=100, blank=True)
    facebook_email = models.EmailField(_('facebook email'),blank=True)
    facebook_expiration_date = models.CharField(_('facebook expiration date'),max_length=35, blank=True)

    yasound_email = models.EmailField(_('email'), blank=True)

    privacy = models.PositiveSmallIntegerField(_('privacy settings'), choices=account_settings.PRIVACY_CHOICES, default=account_settings.PRIVACY_PUBLIC)
    birthday = models.DateField(_('born'), blank=True, null=True)
    gender = models.CharField(_('gender'), max_length=1, choices=account_settings.GENDER_CHOICES, blank=True)

    city = models.CharField(_('city'), max_length=128, blank=True)
    latitude = models.FloatField(null=True, blank=True) # degrees
    longitude = models.FloatField(null=True, blank=True) # degrees

    # latitude and longitude converted to coordinates on a sphere with radius=1
    x_coord = models.FloatField(null=True, blank=True)
    y_coord = models.FloatField(null=True, blank=True)
    z_coord = models.FloatField(null=True, blank=True)

    language = models.CharField(_('language'), max_length=10, choices=yaapp_settings.LANGUAGES, default=yaapp_settings.DEFAULT_USER_LANGUAGE_CODE)

    bio_text = models.TextField(_('bio'), null=True, blank=True)
    picture = ImageField(_('picture'), upload_to=yaapp_settings.USER_PICTURE_FOLDER, null=True, blank=True)
    email_confirmed = models.BooleanField(_('email confirmed'),default=False)
    friends = models.ManyToManyField(User, verbose_name=_('friends'), related_name='friends_profile', null=True, blank=True)
    last_authentication_date = models.DateTimeField(_('last authentication date'),null=True, blank=True)
    notifications_preferences = BitField(flags=(
        'user_in_radio',
        'friend_in_radio',
        'friend_online',
        'message_posted',
        'song_liked',
        'radio_in_favorites',
        'radio_shared',
        'friend_created_radio',
        'fb_share_listen',
        'fb_share_like_song',
        'fb_share_post_message',
        'fb_share_animator_activity',
        'tw_share_listen',
        'tw_share_like_song',
        'tw_share_post_message',
        'tw_share_animator_activity',
        ),
        default=(2+8+16+32+64+128+256+512+1024+2048)
    ) #default = NO (user_in_radio=1) + YES (friend_in_radio=2) + NO (friend_online=4) + YES (message_posted=8) + YES (song_liked=16) + YES (radio_in_favorites=32) + YES (radio_shared=64) + YES (friend_created_radio=128) + YES (fb_share_listen=256) + YES (fb_share_like_song=512) + YES (fb_share_post_message=1024) + YES (fb_share_animator_activity=2048)

    permissions = BitField(flags=(
        'create_radio',
        'hd',
        'selection',
        'geo_create_radio'
        ),
        default=(1)
    ) #defaut = YES (create_radio)

    friends_count = models.IntegerField(default=0)
    followers_count = models.IntegerField(default=0)

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

    @property
    def is_multi_account(self):
        """Return true if account has at least 2 types
        """

        if self.facebook_enabled:
            if self.twitter_enabled or self.yasound_enabled:
                return True
        if self.twitter_enabled:
            if self.facebook_enabled or self.yasound_enabled:
                return True
        if self.yasound_enabled:
            if self.facebook_enabled or self.twitter_enabled:
                return True
        return False

    def convert_to_multi_account_type(self, commit=True):
        """Convert a single account type to a potential multi account type

        Args:
            commit: if true the object is saved
        Returns:
            account_type
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
            accounts = account_type.replace(' ', '').split(account_settings.ACCOUNT_TYPE_SEPARATOR)
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
            if not self.picture:
                self.update_with_social_picture()
        except:
            pass

        account_signals.facebook_account_added.send(sender=self, user=self.user)

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

        # remove social-auth account
        self.user.social_auth.filter(provider='facebook').delete()

        account_signals.facebook_account_removed.send(sender=self, user=self.user)

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
            if not self.picture:
                self.update_with_social_picture()
        except:
            pass

        account_signals.twitter_account_added.send(sender=self, user=self.user)

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

        # remove social-auth account
        self.user.social_auth.filter(provider='twitter').delete()

        account_signals.twitter_account_removed.send(sender=self, user=self.user)

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

        account_signals.yasound_account_added.send(sender=self, user=self.user)

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

        account_signals.yasound_account_removed.send(sender=self, user=self.user)

        return True, _('OK')

    def invite_facebook_friends(self, facebook_ids):
        ia = InvitationsManager()
        ia.add_invitations(self.user.id, InvitationsManager.TYPE_FACEBOOK, facebook_ids)

    def has_invited_twitter_friend(self, twitter_id):
        ia = InvitationsManager()
        return ia.has_invitation(self.user.id, InvitationsManager.TYPE_TWITTER, twitter_id)

    def invite_twitter_friends(self, twitter_ids):
        ia = InvitationsManager()
        ia.add_invitations(self.user.id, InvitationsManager.TYPE_TWITTER, twitter_ids)

    def has_invited_email_friend(self, email):
        ia = InvitationsManager()
        return ia.has_invitation(self.user.id, InvitationsManager.TYPE_EMAIL, email)

    def invite_email_friends(self, emails):
        ia = InvitationsManager()
        ia.add_invitations(self.user.id, InvitationsManager.TYPE_EMAIL, emails)

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
    def hd_expiration_date(self):
        if not self.permissions.hd.is_set:
            return None

        from yapremium.models import UserService
        from yapremium import settings as yapremium_settings
        try:
            us = UserService.objects.get(user=self.user, service__stype=yapremium_settings.SERVICE_HD)
        except UserService.DoesNotExist:
            return None

        return us.expiration_date


    @property
    def own_radio(self):
        radios = self.own_radios(only_ready_radios=False)
        if radios.count() == 0:
            return None
        else:
            return radios[0]

    def own_radios(self, only_ready_radios=True):
        if only_ready_radios:
            radios = Radio.objects.filter(creator=self.user, ready=True, deleted=False)
        else:
            radios = Radio.objects.filter(creator=self.user, deleted=False)
        return radios

    @property
    def current_radio(self):
        current = self.listened_radio
        if not current:
            current = self.connected_radio
        return current if current and current.deleted == False else None

    @property
    def listened_radio(self):
        try:
            r =  RadioUser.objects.filter(user=self.user, listening=True, radio__ready=True, radio__deleted=False)[:1][0].radio
            if not r.is_valid:
                return None
            return r
        except:
            return None

    @property
    def connected_radio(self):
        try:
            r = RadioUser.objects.filter(user=self.user, connected=True, radio__ready=True, radio__deleted=False)[:1][0].radio
            if not r.is_valid:
                return None
            return r
        except:
            return None

    def get_picture_url(self, size='100x100'):
        if self.picture:
            try:
                url = get_thumbnail(self.picture,  size, crop='center', format='JPEG', quality=90).url
            except:
                url = get_thumbnail(yaapp_settings.DEFAULT_IMAGE_PATH, size, crop='center', format='JPEG', quality=90).url
        else:
            url = get_thumbnail(yaapp_settings.DEFAULT_IMAGE_PATH, size, crop='center', format='JPEG', quality=90).url
        return url

    @property
    def picture_url(self):
        """ return picture url (100x100)
        """
        return self.get_picture_url(size='100x100')

    @property
    def large_picture_url(self):
        """ return large picture url (640x640)
        """
        return self.get_picture_url(size='640x640')

    @property
    def small_picture_url(self):
        """ return large picture url (28x28)
        """
        return self.get_picture_url(size='28x28')

    @property
    def age(self):
        bday = self.birthday
        if not bday:
            return None
        d = datetime.date.today()
        return (d.year - bday.year) - int((d.month, d.day) < (bday.month, bday.day))

    def has_friend(self, request_user):
        """
        returns True if request_user is a friend of current user
        """
        if not request_user:
            return False
        if self.friends.filter(id=request_user.id).count() > 0:
            return True
        return False

    def can_give_personal_infos(self, request_user=None):
        if self.privacy == account_settings.PRIVACY_PUBLIC:
            return True
        if request_user and request_user == self.user:
            return True
        if self.privacy == account_settings.PRIVACY_PRIVATE:
            return False
        if self.privacy == account_settings.PRIVACY_FRIENDS:
            if self.has_friend(request_user):
                return True
        return False

    @property
    def connected(self):
        MAX_DELAY_BETWEEN_AUTHENTICATIONS = 10 * 60; # 10 minutes
        alive = False
        if self.last_authentication_date:
            since_last_authentication = datetime.datetime.now() - self.last_authentication_date
            total_seconds = since_last_authentication.days * 86400 + since_last_authentication.seconds
            alive = total_seconds <= MAX_DELAY_BETWEEN_AUTHENTICATIONS
        return alive

    def as_dict(self, request_user=None, include_own_current_radios=False, include_all_radios=False, anonymous_id=None):
        user_id = None
        username = None
        if anonymous_id:
            username = anonymous_id
            user_id = anonymous_id
            if self.name is None:
                self.name = unicode(_('Anonymous user'))
            is_connected = True
        else:
            user_id = self.user.id
            username = self.user.username
            is_connected = self.connected
        data = {
                'id': user_id,
                'picture': self.picture_url,
                'large_picture': self.large_picture_url,
                'name': self.name,
                'username': username,
                'bio_text': self.bio_text[:190] if self.bio_text is not None else None,
                'friends_count': self.friends_count,
                'followers_count': self.followers_count,
                'connected': is_connected,
                'anonymous': True if anonymous_id is not None else False
        }
        if request_user and request_user.id == self.user.id:
            data['owner'] = True
            data['permissions'] = {
                'create_radio': True if self.permissions.create_radio else False,
                'geo_create_radio': True if self.permissions.geo_create_radio else False,
                'hd': True if self.permissions.hd else False,
                'selection': True if self.permissions.selection else False,
            }


        if self.can_give_personal_infos(request_user):
            if self.age is not None:
                data['age'] = self.age
            if self.birthday is not None:
                data['birthday'] = self.birthday
            if self.gender != '':
                data['gender'] = self.gender
            data['city'] = self.city
            data['latitude'] = self.latitude
            data['longitude'] = self.longitude
            data['url'] = self.url
            if request_user and not request_user.is_anonymous():
                p = request_user.get_profile()
                if p:
                    data['is_friend'] = p.has_friend(self.user)

        if include_own_current_radios:
            # own radio (the first one)
            own_radio = self.own_radio
            if own_radio and own_radio.ready and not own_radio.deleted:
                data['own_radio'] = own_radio.as_dict(request_user=request_user)

            # current radio
            current_radio = self.current_radio
            if current_radio and current_radio.ready and not current_radio.deleted:
                data['current_radio'] = current_radio.as_dict(request_user=request_user)

        if include_all_radios:
            # own radios (all)
            own_radios = self.own_radios(only_ready_radios=True)
            own_radios_list = [x.as_dict(request_user=request_user) for x in own_radios]
            data['own_radios'] = own_radios_list

        return data

    def is_complete(self):
        """
        return True if all informations are filled in
        """

        if self.name == '':
            return False

        if self.gender == '':
            return False

        if self.birthday is None:
            return False

        if self.city == '':
            return False

        if self.bio_text is None:
            return False

        if self.bio_text == '':
            return False

        if self.picture is None:
            return False

        return True

    def update_geo_restrictions(self, request):
        country = request_country(request)
        geo_create_radio = yageoperm_utils.can_create_radio(self.user, country)
        if self.permissions.geo_create_radio != geo_create_radio:
            self.permissions.geo_create_radio = geo_create_radio
            self.save()


    def fill_user_bundle(self, bundle, include_own_current_radios=False, include_all_radios=False):
        user_dict = self.as_dict(request_user=bundle.request.user,
                                 include_own_current_radios=include_own_current_radios,
                                 include_all_radios=include_all_radios)
        bundle.data.update(user_dict)

    def fill_user_bundle_with_login_infos(self, bundle):
        self.update_geo_restrictions(bundle.request)

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

    def fill_user_bundle_with_history(self, bundle):
        if not self.user:
            return
        uh = UserHistory()
        doc = uh.last_message(self.user.id)
        if doc is not None:
            radio_uuid = doc.get('data').get('radio_uuid')
            radio_current_song = None
            try:
                radio = Radio.objects.get(uuid=radio_uuid)
                radio_picture = radio.picture_url
                if radio.current_song:
                    radio_current_song = unicode(radio.current_song)[:12]
            except Radio.DoesNotExist:
                radio_picture = settings.DEFAULT_IMAGE

            message = doc.get('data').get('message')
            if message is not None:
                message = message[:120]
            bundle.data['history'] = {
                'date': doc.get('date'),
                'message': message,
                'radio_uuid': radio_uuid,
                'radio_name': doc.get('data').get('radio_name')[:24],
                'radio_picture': radio_picture
            }
            if radio_current_song:
                bundle.data['history']['radio_current_song'] = radio_current_song

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
        if bundle.data.has_key('city'):
            self.city = bundle.data['city']
        if bundle.data.has_key('latitude'):
            self.latitude = bundle.data['latitude']
        if bundle.data.has_key('longitude'):
            self.longitude = bundle.data['longitude']
        if bundle.data.has_key('gender'):
            self.gender = bundle.data['gender']
        if bundle.data.has_key('birthday'):
            birthday = bundle.data['birthday'].split('T')[0]
            self.birthday = birthday
        if bundle.data.has_key('url'):
            self.url = bundle.data['url']

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
            except GraphAPI.FacebookError, e:
                logger.error('GraphAPI exception error: %s' % e)
                return friend_count, yasound_friend_count
            except GraphAPI.HTTPError, e:
                logger.error('GraphAPI exception error (http): %s', e)
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

            for friend in friends:
                self.friends.add(friend)
                # for facebook, relation is bidirectional, so we add the
                # current user as friend of his friends
                friend_profile = friend.get_profile()
                if friend_profile is not None:
                    friend_profile.friends.add(self.user)
            self.update_friends_count(commit=False)
            self.save()

        if self.twitter_enabled:
            auth = tweepy.OAuthHandler(yaapp_settings.YASOUND_TWITTER_APP_CONSUMER_KEY, yaapp_settings.YASOUND_TWITTER_APP_CONSUMER_SECRET)
            auth.set_access_token(self.twitter_token, self.twitter_token_secret)
            api = tweepy.API(auth)
            friends_ids = api.friends_ids()
            friends = User.objects.filter(userprofile__twitter_uid__in=friends_ids)
            for friend in friends:
                self.friends.add(friend)
            self.update_friends_count(commit=False)
            self.save()

        return friend_count, yasound_friend_count

    def add_friend(self, user):
        self.friends.add(user)
        self.update_friends_count()
        try:
            UserProfile.objects.get(user=user).update_friends_count()
        except UserProfile.DoesNotExist:
            pass

    def remove_friend(self, user):
        self.friends.remove(user)
        self.update_friends_count()
        try:
            UserProfile.objects.get(user=user).update_friends_count()
        except UserProfile.DoesNotExist:
            pass

    def update_with_facebook_picture(self):
        if not self.facebook_enabled:
            return
        graph = GraphAPI(self.facebook_token)
        img = graph.get('me/picture?type=large')
        f = ContentFile(img)
        self.set_picture(f)
        # update radios picture
        radios = self.own_radios(only_ready_radios=False)
        for r in radios:
            if not r.picture:
                r.set_picture(f)

    def update_with_twitter_picture(self):
        if not self.twitter_enabled:
            return

        params = {
            'id': self.twitter_uid,
            'size': 'bigger'
        }
        r = requests.get('https://api.twitter.com/1/users/profile_image', params=params)
        f = ContentFile(r.content)
        self.set_picture(f)
        # update radios picture
        radios = self.own_radios(only_ready_radios=False)
        for r in radios:
            if not r.picture:
                r.set_picture(f)

    def update_with_social_picture(self):
        if self.facebook_enabled:
            self.update_with_facebook_picture()
        elif self.twitter_enabled:
            self.update_with_twitter_picture()

    def update_with_social_data(self):
        self.update_with_social_picture()
        self.scan_friends()

    def set_picture(self, data):
        filename = self.build_picture_filename()
        if self.picture and len(self.picture.name) > 0:
            self.picture.delete(save=True)
        self.picture.save(filename, data, save=True)
        delete(self.picture, delete_file=False) # reset sorl-thumbnail cache since the source file has been replaced

    def authenticated(self):
        d = datetime.datetime.now()
        self.last_authentication_date = d
        self.save()

    def check_live_status(self):
        alive = self.connected
        if not alive:
            RadioUser.objects.filter(user=self.user, connected=True).update(connected=False)
            RadioUser.objects.filter(user=self.user, listening=True).update(listening=False)
        return alive

    def build_fuzzy_index(self, upsert=False, insert=True):
        return yasearch_indexer.add_user(self.user, upsert, insert)

    def remove_from_fuzzy_index(self):
        return yasearch_indexer.remove_user(self.user)

    def save(self, *args, **kwargs):
        creation = self.pk is None
        update_mongo = False
        coords_changed = creation
        if not creation:
            saved = UserProfile.objects.get(pk=self.pk)
            name_changed = self.name != saved.name
            update_mongo = name_changed
            coords_changed = (self.latitude != saved.latitude) or (self.longitude != saved.longitude)

        super(UserProfile, self).save(*args, **kwargs)
        if update_mongo:
            self.build_fuzzy_index(upsert=True)
        if coords_changed:
            self.position_changed()

    def build_picture_filename(self):
        filename = 'userprofile_%d_picture.png' % self.id
        return filename

    def radio_is_ready(self, radio):
        for f in self.friends.all():
            try:
                friend_profile = f.get_profile()
                friend_profile.my_friend_created_radio(self, radio)
            except:
                pass

    def logged(self, request=None):
        for f in self.friends.all():
            try:
                friend_profile = f.get_profile()
                friend_profile.my_friend_is_online(self)
            except:
                pass
        if request is not None:
            self.check_geo_localization(request)

    def add_to_group(self, group_name):
        g, _created = Group.objects.get_or_create(name=group_name)
        g.user_set.add(self.user)

    def send_message(self, sender, message, radio=None):
        m = NotificationsManager()
        custom_params = {
            'sender_id': sender.id,
            'text': message
        }
        m.add_notification(recipient_user_id=self.user.id,
                           notif_type=yamessage_settings.TYPE_NOTIF_MESSAGE_FROM_USER,
                           params=message,
                           from_user_id=sender.id,
                           from_radio_id=radio.id if radio is not None else None,
                           language=self.language)

        self.send_APNs_message(message=message,
                               custom_params={
                                    yamessage_settings.YASOUND_NOTIF_PARAMS_ATTRIBUTE_NAME:custom_params
                               },
                               loc_key=yamessage_settings.APNS_LOC_KEY_MESSAGE_FROM_USER,
                               loc_args=[sender.get_profile().name])


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
        if friend_profile == self:
            return
        if self.connected_radio == radio:
            return
        custom_params = {}
        custom_params['user_id'] = friend_profile.user.id
        custom_params['radio_id'] = radio.id


        # store notification
        notif_params = {
            'user_name': unicode(friend_profile),
            'user_id': friend_profile.user.id,
            'user_username': friend_profile.user.username,
            'radio_id': radio.id,
            'radio_uuid': radio.uuid,
            'radio_name': radio.name,
        }
        m = NotificationsManager()
        m.add_notification(self.user.id,
                           yamessage_settings.TYPE_NOTIF_FRIEND_IN_RADIO,
                           notif_params,
                           from_radio_id=radio.id,
                           language=self.language)

        if not self.notifications_preferences.friend_in_radio:
            return
        # send APNs notification
        self.send_APNs_message(message=None, custom_params={YASOUND_NOTIF_PARAMS_ATTRIBUTE_NAME:custom_params}, loc_key=yamessage_settings.APNS_LOC_KEY_FRIEND_IN_RADIO, loc_args=[friend_profile.name])

    def _user_in_my_radio_internal(self, user_profile, radio):
        if user_profile == self:
            return
        if self.connected_radio == radio:
            return
        custom_params = {}
        custom_params['user_id'] = user_profile.user.id
        custom_params['radio_id'] = radio.id

        # store notification
        notif_params = {
            'user_name': unicode(user_profile),
            'user_id': user_profile.user.id,
            'user_username': user_profile.user.username,
            'radio_id': radio.id,
            'radio_uuid': radio.uuid,
            'radio_name': radio.name,
        }
        m = NotificationsManager()
        m.add_notification(self.user.id,
                           yamessage_settings.TYPE_NOTIF_USER_IN_RADIO,
                           notif_params,
                           from_radio_id=radio.id,
                           language=self.language)

        if not self.notifications_preferences.user_in_radio:
            return
        # send APNs notification
        self.send_APNs_message(message=None, custom_params={YASOUND_NOTIF_PARAMS_ATTRIBUTE_NAME:custom_params}, loc_key=yamessage_settings.APNS_LOC_KEY_USER_IN_RADIO, loc_args=[user_profile.name])


    def my_friend_is_online(self, friend_profile):
        if friend_profile == self:
            return
        custom_params = {}
        custom_params['user_id'] = friend_profile.user.id

        # store notification
        m = NotificationsManager()

        last_notifications = m.notifications.find({'type': yamessage_settings.TYPE_NOTIF_FRIEND_ONLINE}).sort([('date', DESCENDING)]).limit(1)
        if last_notifications.count() > 0:
            last_notification = last_notifications[0]
            last_notification_date = last_notification.get('date')
            now = datetime.datetime.now()
            diff = (now - last_notification_date)
            total_seconds = diff.days * 86400 + diff.seconds
            if total_seconds < 60*60:
                last_notification['date'] = now
                m.update_notification(last_notification)
                return

        notif_params = {
            'user_name': unicode(friend_profile),
            'user_id': friend_profile.user.id,
            'user_username': friend_profile.user.username,
        }
        m.add_notification(self.user.id,
                           yamessage_settings.TYPE_NOTIF_FRIEND_ONLINE,
                           notif_params,
                           language=self.language)

        if not self.notifications_preferences.friend_online:
            return
        # send APNs notification
        self.send_APNs_message(message=None, custom_params={YASOUND_NOTIF_PARAMS_ATTRIBUTE_NAME:custom_params}, loc_key=yamessage_settings.APNS_LOC_KEY_FRIEND_ONLINE, loc_args=[friend_profile.name])

    def message_posted_in_my_radio(self, wall_message):
        user_profile = wall_message.user.get_profile()
        radio = wall_message.radio

        if user_profile == self:
            return
        if self.connected_radio == radio:
            return
        custom_params = {}
        custom_params['uID'] = user_profile.user.id
        custom_params['rID'] = radio.id

        # store notification
        notif_params = {
            'user_name': unicode(user_profile),
            'user_id': user_profile.user.id,
            'user_username': user_profile.user.username,
            'radio_id': radio.id,
            'radio_uuid': radio.uuid,
            'radio_name': radio.name,
        }
        m = NotificationsManager()
        m.add_notification(self.user.id,
                           yamessage_settings.TYPE_NOTIF_MESSAGE_IN_WALL,
                           notif_params,
                           from_radio_id=radio.id,
                           language=self.language)

        if not self.notifications_preferences.message_posted:
            return
        # send APNs notification
        self.send_APNs_message(message=None, custom_params={YASOUND_NOTIF_PARAMS_ATTRIBUTE_NAME:custom_params}, loc_key=yamessage_settings.APNS_LOC_KEY_MESSAGE_IN_WALL, loc_args=[user_profile.name])

    def song_liked_in_my_radio(self, user_profile, radio, song):
        if user_profile == self:
            return
        if self.connected_radio == radio:
            return
        custom_params = {}
        custom_params['uID'] = user_profile.user.id
        custom_params['rID'] = radio.id
        custom_params['sID'] = song.id

        # store notification
        notif_params = {
            'user_name': unicode(user_profile),
            'song_name': unicode(song),
            'user_id': user_profile.user.id,
            'radio_id': radio.id,
            'radio_uuid': radio.uuid,
            'radio_name': radio.name,
            'song_id': song.id,
            'user_username': user_profile.user.username,
        }
        m = NotificationsManager()
        m.add_notification(self.user.id,
                           yamessage_settings.TYPE_NOTIF_SONG_LIKED,
                           notif_params,
                           from_radio_id=radio.id,
                           language=self.language)

        if not self.notifications_preferences.song_liked:
            return
        # send APNs notification
        self.send_APNs_message(message=None, custom_params={YASOUND_NOTIF_PARAMS_ATTRIBUTE_NAME:custom_params}, loc_key=yamessage_settings.APNS_LOC_KEY_SONG_LIKED, loc_args=[user_profile.name, song.metadata.name])

    def my_radio_added_in_favorites(self, user_profile, radio):
        if user_profile == self:
            return
        custom_params = {}
        custom_params['uID'] = user_profile.user.id
        custom_params['rID'] = radio.id

        # store notification
        notif_params = {
            'user_name': unicode(user_profile),
            'user_id': user_profile.user.id,
            'user_username': user_profile.user.username,
            'radio_id': radio.id,
            'radio_name': radio.name,
            'radio_uuid': radio.uuid,
        }
        m = NotificationsManager()
        m.add_notification(self.user.id,
                           yamessage_settings.TYPE_NOTIF_RADIO_IN_FAVORITES,
                           notif_params,
                           from_radio_id=radio.id,
                           language=self.language)

        if not self.notifications_preferences.radio_in_favorites:
            return
        # send APNs notification
        self.send_APNs_message(message=None, custom_params={YASOUND_NOTIF_PARAMS_ATTRIBUTE_NAME:custom_params}, loc_key=yamessage_settings.APNS_LOC_KEY_RADIO_IN_FAVORITES, loc_args=[user_profile.name])

    def my_radio_shared(self, user_profile, radio):
        if user_profile == self:
            return
        custom_params = {}
        custom_params['uID'] = user_profile.user.id
        custom_params['rID'] = radio.id

        # store notification
        notif_params = {
            'user_name': unicode(user_profile),
            'user_id': user_profile.user.id,
            'user_username': user_profile.user.username,
            'radio_id': radio.id,
            'radio_uuid': radio.uuid,
            'radio_name': radio.name,
        }
        m = NotificationsManager()
        m.add_notification(self.user.id,
                           yamessage_settings.TYPE_NOTIF_RADIO_SHARED,
                           notif_params,
                           from_radio_id=radio.id,
                           language=self.language)

        if not self.notifications_preferences.radio_shared:
            return
        # send APNs notification
        self.send_APNs_message(message=None, custom_params={YASOUND_NOTIF_PARAMS_ATTRIBUTE_NAME:custom_params}, loc_key=yamessage_settings.APNS_LOC_KEY_RADIO_SHARED, loc_args=[user_profile.name])

    def my_friend_created_radio(self, friend_profile, radio):
        custom_params = {}
        custom_params['uID'] = friend_profile.user.id
        custom_params['rID'] = radio.id

        # store notification
        notif_params = {
            'user_name': unicode(friend_profile),
            'user_username': friend_profile.user.username,
            'user_id': friend_profile.user.id,
            'radio_id': radio.id,
            'radio_uuid': radio.uuid,
            'radio_name': radio.name,
        }
        m = NotificationsManager()
        m.add_notification(self.user.id,
                           yamessage_settings.TYPE_NOTIF_FRIEND_CREATED_RADIO,
                           notif_params,
                           from_radio_id=radio.id,
                           language=self.language)

        if not self.notifications_preferences.friend_created_radio:
            return
        # send APNs notification
        self.send_APNs_message(message=None, custom_params={YASOUND_NOTIF_PARAMS_ATTRIBUTE_NAME:custom_params}, loc_key=yamessage_settings.APNS_LOC_KEY_FRIEND_CREATED_RADIO, loc_args=[friend_profile.name])

    def message_from_yasound(self, url_param):
        custom_params = {}
        custom_params['url'] = url_param

        # store notification
        m = NotificationsManager()
        m.add_notification(self.user.id,
                           yamessage_settings.TYPE_NOTIF_MESSAGE_FROM_YASOUND,
                           params=custom_params,
                           language=self.language)

        # send APNs notification
        self.send_APNs_message(message=None, custom_params={YASOUND_NOTIF_PARAMS_ATTRIBUTE_NAME:custom_params}, loc_key=yamessage_settings.APNS_LOC_KEY_MESSAGE_FROM_YASOUND)


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


    def facebook_share_preferences(self):
        prefs = {
                 'fb_share_listen':             True if self.notifications_preferences.fb_share_listen else False,
                 'fb_share_like_song':          True if self.notifications_preferences.fb_share_like_song else False,
                 'fb_share_post_message':       True if self.notifications_preferences.fb_share_post_message else False,
                 'fb_share_animator_activity':  True if self.notifications_preferences.fb_share_animator_activity else False,
                 }
        return prefs

    def set_facebook_share_preferences(self, pref_dict):
        fb_share_listen             = pref_dict.get('fb_share_listen', None)
        fb_share_like_song          = pref_dict.get('fb_share_like_song', None)
        fb_share_post_message       = pref_dict.get('fb_share_post_message', None)
        fb_share_animator_activity  = pref_dict.get('fb_share_animator_activity', None)

        if fb_share_listen is not None:
            self.notifications_preferences.fb_share_listen = fb_share_listen
        if fb_share_like_song is not None:
            self.notifications_preferences.fb_share_like_song = fb_share_like_song
        if fb_share_post_message is not None:
            self.notifications_preferences.fb_share_post_message = fb_share_post_message
        if fb_share_animator_activity is not None:
            self.notifications_preferences.fb_share_animator_activity = fb_share_animator_activity
        self.save()

    def twitter_share_preferences(self):
        prefs = {
                 'tw_share_listen':             True if self.notifications_preferences.tw_share_listen else False,
                 'tw_share_like_song':          True if self.notifications_preferences.tw_share_like_song else False,
                 'tw_share_post_message':       True if self.notifications_preferences.tw_share_post_message else False,
                 'tw_share_animator_activity':  True if self.notifications_preferences.tw_share_animator_activity else False,
                 }
        return prefs

    def set_twitter_share_preferences(self, pref_dict):
        tw_share_listen             = pref_dict.get('tw_share_listen', None)
        tw_share_like_song          = pref_dict.get('tw_share_like_song', None)
        tw_share_post_message       = pref_dict.get('tw_share_post_message', None)
        tw_share_animator_activity  = pref_dict.get('tw_share_animator_activity', None)

        if tw_share_listen is not None:
            self.notifications_preferences.tw_share_listen = tw_share_listen
        if tw_share_like_song is not None:
            self.notifications_preferences.tw_share_like_song = tw_share_like_song
        if tw_share_post_message is not None:
            self.notifications_preferences.tw_share_post_message = tw_share_post_message
        if tw_share_animator_activity is not None:
            self.notifications_preferences.tw_share_animator_activity = tw_share_animator_activity
        self.save()

    def set_position(self, lat, lon, unit='degrees'):
        if unit == 'radians':
            lat = math.degrees(lat) # to degrees
            lon = math.degrees(lon) # to degrees
        self.latitude = lat
        self.longitude = lon
        self.save()

    def connected_userprofiles(self, skip=0, limit=20, formula_type='chord', time_condition_enabled=True):
        lat = self.latitude
        lon = self.longitude
        return UserProfile.objects.connected_userprofiles(ref_lat=lat, ref_lon=lon, skip=skip, limit=limit, exclude_profile=self, formula_type=formula_type, time_condition_enabled=time_condition_enabled)



    def check_geo_localization(self, request):
        from task import async_check_geo_localization
        async_check_geo_localization.delay(userprofile=self, ip=request.META[yaapp_settings.GEOIP_LOOKUP])

    def position_changed(self):
        if self.latitude is None or self.longitude is None:
            return
        self.update_position_coords()

    def update_position_coords(self, save=True):
        coords = latitude_longitude_to_coords(self.latitude, self.longitude, 'degrees')
        UserProfile.objects.filter(id=self.id).update(x_coord=coords[0], y_coord=coords[1], z_coord=coords[2])

    def web_preferences(self):
        ua = UserAdditionalInfosManager()
        information = ua.information(self.user.id)
        if information is None:
            return {}
        else:
            return information.get('web_preferences', {})

    def set_web_preferences(self, preference, value):
        preferences = self.web_preferences()
        preferences[preference] = value
        ua = UserAdditionalInfosManager()
        ua.add_information(self.user.id, 'web_preferences', preferences)

    def update_friends_count(self, commit=True):
        self.friends_count = self.friends.count()
        self.followers_count = UserProfile.objects.filter(friends=self.user).count()
        if commit:
            self.save()

    @property
    def has_radios(self):
        """return True if profile has at least one radio"""
        try:
            self.user.radio_set.all()[0]
            return True
        except:
            return False

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        _profile, _created = UserProfile.objects.get_or_create(user=instance)


def create_ml_contact(sender, instance, created, **kwargs):
    if created:
        from emencia.django.newsletter.models import Contact
        from emencia.django.newsletter.models import MailingList
        email = instance.user.email
        first_name = ''
        last_name = instance.name
        if email is not None and len(email) > 0:
            contact, _created = Contact.objects.get_or_create(email=email,
                                                             defaults={'first_name': first_name,
                                                                       'last_name': last_name,
                                                                       'content_object': instance,
                                                                       'verified': True})
            mailing, created = MailingList.objects.get_or_create(name='all',
                                      defaults={'description': 'All users'})
            mailing.subscribers.add(contact)


def get_techtour_group():
    g, _created = Group.objects.get_or_create(name=yabase_settings.TECH_TOUR_GROUP_NAME)
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

        device, _created = self.get_or_create(user=user, ios_token=device_token)
        device.uuid = device_uuid
        device.ios_token_type=device_token_type
        device.application_identifier=app_identifier
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
    ios_token_type = models.CharField(_('ios token type'), max_length=16, choices=account_settings.IOS_TOKEN_TYPE_CHOICES)
    registration_date = models.DateTimeField(_('registration date'), auto_now_add=True)
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
            account_signals.new_device_registered.send(sender=self, user=self.user, uuid=self.uuid, ios_token=self.ios_token)
            Device.objects.filter(ios_token=self.ios_token, application_identifier=self.application_identifier).exclude(user=self.user).delete() # be sure to 'forget' old registrations for this device

    def __unicode__(self):
        return u'%s - %s - %s (%s)' % (self.user.get_profile().name, self.application_identifier, self.ios_token, self.ios_token_type);

class UserAdditionalInfosManager():

    def __init__(self):
        self.db = settings.MONGO_DB
        self.collection = self.db.account.users
        self.collection.ensure_index('db_id', unique=True)

    def erase_informations(self):
        self.collection.drop()

    def add_information(self, user_id, information_key, data):
        self.collection.update({'db_id': user_id}, {'$set': {information_key: data}}, upsert=True, safe=True)

    def remove_information(self, user_id, information_key):
        self.collection.update({'db_id': user_id}, {'$unset': {information_key: 1}}, upsert=True, safe=True)

    def information(self, user_id):
        return self.collection.find_one({'db_id': user_id})

    def remove_user(self, user_id):
        self.collection.remove({'db_id': user_id})


class InvitationsManager():

    TYPE_FACEBOOK = 'facebook'
    TYPE_TWITTER = 'twitter'
    TYPE_EMAIL = 'email'

    def __init__(self):
        self.db = settings.MONGO_DB
        self.collection = self.db.account.users.invitations
        self.collection.ensure_index('db_id', unique=True)
        self.collection.ensure_index(InvitationsManager.TYPE_FACEBOOK)
        self.collection.ensure_index(InvitationsManager.TYPE_TWITTER)
        self.collection.ensure_index(InvitationsManager.TYPE_EMAIL)

    def erase_informations(self):
        self.collection.drop()

    def add_invitations(self, user_id, type, uids):
        self.collection.update({'db_id': user_id}, {'$addToSet': {type: {'$each': uids} } }, upsert=True, safe=True)

    def remove_invitation(self, user_id, type, uid):
        self.collection.update({'db_id': user_id}, {'$pull': {type: uid}}, upsert=True, safe=True)

    def has_invitation(self, user_id, type, uid):
        if self.collection.find_one({'db_id': user_id, type:uid}):
            return True
        return False

    def find_invitation_providers(self, type, uid):
        db_ids = self.collection.find({type:uid}, {'db_id': True, '_id': False})
        return db_ids

class AnonymousManager():
    """Store anonymous users data in mongodb
    """
    ANONYMOUS_TTL = 20 # seconds

    def __init__(self):
        self.db = settings.MONGO_DB
        self.collection = self.db.account.users.anonymous
        self.collection.ensure_index('radio_uuid')
        self.collection.ensure_index('anonymous_id', unique=True)
        self.collection.ensure_index('updated')

    def erase_informations(self):
        self.collection.drop()

    def upsert_anonymous(self, anonymous_id, radio_uuid, city_record=None):
        """insert or update an anonymous user

        :param anonymous_id: a unique anonymous id
        :param radio_uuid: radio uuid
        :param city_record: geoip record
        """

        now = datetime.datetime.now()
        doc = {
            'anonymous_id': anonymous_id,
            'radio_uuid': radio_uuid,
            'city_record': city_record,
            'updated': now
        }
        self.collection.update({'anonymous_id': anonymous_id}, {'$set': doc }, upsert=True, safe=True)

    def anonymous_for_radio(self, radio_uuid):
        """return the anonymous users for a given radio

        a list of::

        doc = {
            'anonymous_id': anonymous_id,
            'radio_uuid': radio_uuid,
            'city_record': city_record,
            'updated': now
        }
        """

        now = datetime.datetime.now()
        expired_date = now + relativedelta(seconds=-AnonymousManager.ANONYMOUS_TTL)
        return self.collection.find({
            'radio_uuid': radio_uuid,
            'updated': {
                '$gte': expired_date
            }
        })

    def remove_inactive_users(self):
        """deleted expired anonymous users"""

        now = datetime.datetime.now()
        expired_date = now + relativedelta(seconds=-AnonymousManager.ANONYMOUS_TTL)
        self.collection.remove({'updated': {'$lt': expired_date}}, safe=True)


def user_profile_deleted(sender, instance, created=None, **kwargs):
    if isinstance(instance, UserProfile):
        user_profile = instance
    else:
        return

    ua = UserAdditionalInfosManager()
    ua.remove_user(user_profile.user.id)
    user_profile.remove_from_fuzzy_index()

def new_wall_event_handler(sender, wall_event, **kwargs):
    user = wall_event.user
    if user is None:
        return
    if user.is_anonymous():
        return

    we_type = wall_event.type
    if we_type == yabase_settings.EVENT_MESSAGE:
        if not user.get_profile().notifications_preferences.tw_share_post_message:
            return
        async_tw_post_message.delay(user.id, wall_event.radio.uuid, wall_event.text)
    elif we_type == yabase_settings.EVENT_LIKE:
        if not user.get_profile().notifications_preferences.tw_share_like_song:
            return
        song_title = wall_event.song.metadata.name
        artist = wall_event.song.metadata.artist_name
        async_tw_like_song.delay(user.id, wall_event.radio.uuid, song_title, artist)

def user_started_listening_song_handler(sender, radio, user, song, **kwargs):
    """
    Publish listening event on twitter
    """
    if user is None:
        return
    if user.is_anonymous():
        return
    if song is None:
        return

    if not user.get_profile().notifications_preferences.tw_share_listen:
        return

    song_title = unicode(song)
    artist =  song.metadata.artist_name
    async_tw_listen.delay(user.id, radio.uuid, song_title, artist)

def new_animator_activity(sender, user, radio, **kwargs):
    """
    Publish animator activity on twitter
    """
    if user is None or radio is None:
        return
    if user.is_anonymous():
        return

    if not user.get_profile().notifications_preferences.tw_share_animator_activity:
        return

    async_tw_animator_activity.delay(user.id, radio.uuid)


def new_social_user(sender, user, response, details, **kwargs):
    backend_name = sender.name.lower()
    if backend_name == 'twitter':
        access_token = response.get('access_token')
        tokens = dict(tok.split('=') for tok in access_token.split('&'))
        token = tokens.get('oauth_token')
        token_secret = tokens.get('oauth_token_secret')

        profile = user.get_profile()
        profile.twitter_token = token
        profile.twitter_token_secret = token_secret
        profile.save()
    elif backend_name == 'facebook':
        access_token = response.get('access_token')
        profile = user.get_profile()
        profile.facebook_token = access_token
        profile.save()

def social_user_updated(sender, instance, created=None, **kwargs):
    if instance.extra_data is None or len(instance.extra_data) == 0:
        return

    response = instance.extra_data
    backend_name = instance.provider.lower()
    user = instance.user

    if backend_name == 'twitter':
        access_token = response.get('access_token')
        tokens = dict(tok.split('=') for tok in access_token.split('&'))
        token = tokens.get('oauth_token', '')
        token_secret = tokens.get('oauth_token_secret', '')

        profile = user.get_profile()
        if len(token) > 0:
            profile.twitter_token = token
        if len(token_secret) > 0:
            profile.twitter_token_secret = token_secret
        profile.save()
    elif backend_name == 'facebook':
        access_token = response.get('access_token', '')
        profile = user.get_profile()
        if len(access_token) > 0:
            profile.facebook_token = access_token
        profile.save()

def new_radio_created(sender, instance, created=None, **kwargs):
    if not created:
        return
    radio = instance
    user = radio.creator
    if not user:
        return

    if user.is_superuser:
        return
    radio_count = Radio.objects.filter(creator=user).count()

    if radio_count >= yaapp_settings.MAX_RADIO_PER_USER:
        profile = user.get_profile()
        profile.permissions.create_radio = False
        profile.save()

def check_for_language(sender, request, user, **kwargs):
    if not hasattr(request, 'LANGUAGE_CODE'):
        return

    p = user.get_profile()
    if p is None:
        return


    if p.language != request.LANGUAGE_CODE and request.LANGUAGE_CODE in yaapp_settings.ALLOWED_LANGUAGES:
        p.language = request.LANGUAGE_CODE
        p.save()

def install_handlers():
    post_save.connect(create_user_profile, sender=User)
    post_save.connect(create_user_profile, sender=EmailUser)
    post_save.connect(create_api_key, sender=User)
    post_save.connect(create_api_key, sender=EmailUser)
    post_save.connect(create_ml_contact, sender=UserProfile)
    post_save.connect(new_radio_created, sender=Radio)
    pre_delete.connect(user_profile_deleted, sender=UserProfile)

    yabase_signals.new_wall_event.connect(new_wall_event_handler)
    yabase_signals.user_started_listening_song.connect(user_started_listening_song_handler)
    yabase_signals.new_animator_activity.connect(new_animator_activity)

    socialauth_registered.connect(new_social_user)
    post_save.connect(social_user_updated, sender=UserSocialAuth)

    auth_signals.user_logged_in.connect(check_for_language)

install_handlers()

