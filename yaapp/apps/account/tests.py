from account.models import UserProfile, Device
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils import simplejson as json
from tastypie.models import ApiKey
from yabase import tests_utils as yabase_tests_utils
from yabase.models import Radio, RadioUser
from yasearch.indexer import erase_index
import settings as account_settings
import task
import yabase.settings as yabase_settings
from django.conf import settings
import datetime
from models import UserAdditionalInfosManager, InvitationsManager, AnonymousManager
from yamessage.models import NotificationsManager
from yamessage import settings as yamessage_settings
from pymongo import DESCENDING
from django.test.client import RequestFactory
from yacore.http import is_iphone_version_1, is_iphone_version_2
from yabase.models import SongInstance, SongMetadata, WallEvent
from dateutil.relativedelta import *

class TestProfile(TestCase):
    def setUp(self):
        ua = UserAdditionalInfosManager()
        ua.erase_informations()

        erase_index()

    def test_profile_creation(self):
        user = User(email="test@yasound.com", username="test", is_superuser=False, is_staff=False)
        user.set_password('test')
        user.save()
        self.assertEqual(user.get_profile(), UserProfile.objects.get(id=1))

        user_dict = user.get_profile().as_dict(request_user=user)
        permissions = user_dict.get('permissions')
        self.assertTrue(permissions.get('create_radio'))

    def test_age_gender_privacy(self):
        user = User(email="test@yasound.com", username="test", is_superuser=False, is_staff=False)
        user.set_password('test')
        user.save()

        profile = user.get_profile()
        self.assertIsNone(profile.age)
        self.assertIsNone(profile.birthday)
        self.assertEquals(profile.gender, '')
        self.assertEquals(profile.privacy, account_settings.PRIVACY_PUBLIC)

        profile.birthday = datetime.date(2007, 01, 01)
        self.assertTrue(profile.age >= 5)

    def test_additional_info(self):
        user = User(email="test@yasound.com", username="test", is_superuser=False, is_staff=False)
        user.set_password('test')
        user.save()
        self.assertEqual(user.get_profile(), UserProfile.objects.get(id=1))

        info = ['deezer', 'soundclound']

        ua = UserAdditionalInfosManager()
        ua.add_information(user.id, 'connected_account', info)

        doc = ua.information(user.id)
        self.assertEquals(doc.get('connected_account'), ['deezer', 'soundclound'])

        info = {
            'token': 'token1',
            'expiration': 'no-expiration'
        }
        ua.add_information(user.id, 'deezer', info)

        doc = ua.information(user.id)
        self.assertEquals(doc.get('connected_account'), ['deezer', 'soundclound'])
        self.assertEquals(doc.get('deezer').get('token'), 'token1')

        ua.remove_information(user.id, 'deezer')
        doc = ua.information(user.id)
        self.assertEquals(doc.get('connected_account'), ['deezer', 'soundclound'])
        self.assertIsNone(doc.get('deezer'))

    def test_privacy(self):
        user1 = User.objects.create(email="user1@yasound.com", username="user1", is_superuser=False, is_staff=False)
        user2 = User.objects.create(email="user2@yasound.com", username="user2", is_superuser=False, is_staff=False)

        profile1 = user1.get_profile()
        profile2 = user2.get_profile()

        self.assertTrue(profile1.can_give_personal_infos())
        self.assertTrue(profile1.can_give_personal_infos(user2))
        self.assertTrue(profile2.can_give_personal_infos())

        profile1.privacy = account_settings.PRIVACY_PRIVATE
        profile1.save()

        self.assertFalse(profile1.can_give_personal_infos(user2))
        self.assertTrue(profile1.can_give_personal_infos(user1))

        profile1.add_friend(user2)
        self.assertFalse(profile1.can_give_personal_infos(user2))

        profile1.privacy = account_settings.PRIVACY_FRIENDS
        profile1.save()

        self.assertTrue(profile1.can_give_personal_infos(user2))

    def test_friends(self):
        user1 = User.objects.create(email="user1@yasound.com", username="user1", is_superuser=False, is_staff=False)
        user2 = User.objects.create(email="user2@yasound.com", username="user2", is_superuser=False, is_staff=False)

        profile1 = user1.get_profile()
        profile2 = user2.get_profile()
        self.assertEquals(profile1.friends_count, 0)
        self.assertEquals(profile1.followers_count, 0)

        profile2.add_friend(user1)

        profile1 = UserProfile.objects.get(id=profile1.id)
        profile2 = UserProfile.objects.get(id=profile2.id)

        self.assertEquals(profile1.friends_count, 0)
        self.assertEquals(profile1.followers_count, 1)
        self.assertEquals(profile2.friends_count, 1)

        profile2.remove_friend(user1)

        profile1 = UserProfile.objects.get(id=profile1.id)
        profile2 = UserProfile.objects.get(id=profile2.id)

        self.assertEquals(profile1.friends_count, 0)
        self.assertEquals(profile1.followers_count, 0)
        self.assertEquals(profile2.friends_count, 0)

        profile1.add_friend(user2)

        profile1 = UserProfile.objects.get(id=profile1.id)
        profile2 = UserProfile.objects.get(id=profile2.id)

        self.assertEquals(profile1.friends_count, 1)
        self.assertEquals(profile2.followers_count, 1)
        self.assertEquals(profile2.friends_count, 0)

    def test_index_fuzzy(self):
        user = User(email="test@yasound.com", username="username", is_superuser=False, is_staff=False)
        user.save()
        profile = user.get_profile()
        profile.name = 'username'
        profile.save()

        users = UserProfile.objects.search_user_fuzzy('username')
        self.assertEquals(len(users), 1)

        users = UserProfile.objects.search_user_fuzzy('babar')
        self.assertEquals(len(users), 0)

        user = User(email="other@yasound.com", username="babar", is_superuser=False, is_staff=False)
        user.save()
        profile = user.get_profile()
        profile.name = 'babar'
        profile.save()

        users = UserProfile.objects.search_user_fuzzy('babar')
        self.assertEquals(len(users), 1)

    def test_index_fuzzy_delete(self):
        user = User(email="test@yasound.com", username="username", is_superuser=False, is_staff=False)
        user.save()

        profile = user.get_profile()
        profile.name = 'username'
        profile.save()

        user = User(email="other@yasound.com", username="babar", is_superuser=False, is_staff=False)
        user.save()
        profile = user.get_profile()
        profile.name = 'babar'
        profile.save()

        User.objects.get(id=1).delete()

        users = UserProfile.objects.search_user_fuzzy('username')
        self.assertEquals(len(users), 0)

        users = UserProfile.objects.search_user_fuzzy('babar')
        self.assertEquals(len(users), 1)

    def test_permissions_create_radio(self):
        user1 = User.objects.create(email="user1@yasound.com", username="user1", is_superuser=False, is_staff=False)
        profile1 = user1.get_profile()
        self.assertTrue(profile1.permissions.create_radio)

        radios = Radio.objects.filter(creator=user1)
        self.assertEquals(radios.count(), 0)

        for i in range(0, settings.MAX_RADIO_PER_USER + 1):
            Radio.objects.create(creator=user1)

        profile1 = UserProfile.objects.get(id=profile1.id)
        self.assertFalse(profile1.permissions.create_radio)


class TestMultiAccount(TestCase):
    def setUp(self):
        erase_index()

        # jbl
        jerome = User(email="jbl@yasound.com", username="jerome", is_superuser=False, is_staff=False)
        jerome.set_password('jerome')
        jerome.save()
        self.assertEqual(jerome.get_profile(), UserProfile.objects.get(id=1))
        self.jerome = jerome

    def test_convert(self):
        profile = self.jerome.get_profile()
        profile.account_type = account_settings.ACCOUNT_TYPE_FACEBOOK
        profile.save()

        self.assertTrue(profile.facebook_enabled)
        self.assertFalse(profile.twitter_enabled)
        self.assertFalse(profile.yasound_enabled)

        profile.convert_to_multi_account_type()
        self.assertEquals(profile.account_type, account_settings.ACCOUNT_MULT_FACEBOOK)

        self.assertTrue(profile.facebook_enabled)
        self.assertFalse(profile.twitter_enabled)
        self.assertFalse(profile.yasound_enabled)

    def test_multi_add(self):
        profile = self.jerome.get_profile()
        profile.account_type = account_settings.ACCOUNT_MULT_FACEBOOK
        profile.save()
        profile.add_account_type(account_settings.ACCOUNT_MULT_TWITTER)
        self.assertEquals(profile.account_type, account_settings.ACCOUNT_MULT_FACEBOOK + account_settings.ACCOUNT_TYPE_SEPARATOR + account_settings.ACCOUNT_MULT_TWITTER)

        self.assertTrue(profile.facebook_enabled)
        self.assertTrue(profile.twitter_enabled)
        self.assertFalse(profile.yasound_enabled)

    def test_multi_add_from_none(self):
        profile = self.jerome.get_profile()
        profile.account_type = None
        profile.add_account_type(account_settings.ACCOUNT_MULT_TWITTER)
        self.assertEquals(profile.account_type, account_settings.ACCOUNT_MULT_TWITTER)

        self.assertFalse(profile.facebook_enabled)
        self.assertTrue(profile.twitter_enabled)
        self.assertFalse(profile.yasound_enabled)

        profile.add_account_type(account_settings.ACCOUNT_MULT_TWITTER)
        self.assertEquals(profile.account_type, account_settings.ACCOUNT_MULT_TWITTER)

    def test_multi_remove(self):
        profile = self.jerome.get_profile()
        profile.account_type = account_settings.ACCOUNT_MULT_FACEBOOK
        profile.save()
        profile.add_account_type(account_settings.ACCOUNT_MULT_TWITTER)
        self.assertEquals(profile.account_type, account_settings.ACCOUNT_MULT_FACEBOOK + account_settings.ACCOUNT_TYPE_SEPARATOR + account_settings.ACCOUNT_MULT_TWITTER)

        self.assertTrue(profile.facebook_enabled)
        self.assertTrue(profile.twitter_enabled)
        self.assertFalse(profile.yasound_enabled)

        profile.remove_account_type(account_settings.ACCOUNT_MULT_FACEBOOK)
        self.assertEquals(profile.account_type, account_settings.ACCOUNT_MULT_TWITTER)

        self.assertFalse(profile.facebook_enabled)
        self.assertTrue(profile.twitter_enabled)
        self.assertFalse(profile.yasound_enabled)

    def test_multi_from_old(self):
        profile = self.jerome.get_profile()
        profile.account_type = account_settings.ACCOUNT_TYPE_FACEBOOK
        profile.save()
        profile.add_account_type(account_settings.ACCOUNT_MULT_TWITTER)
        self.assertEquals(profile.account_type, account_settings.ACCOUNT_MULT_FACEBOOK + account_settings.ACCOUNT_TYPE_SEPARATOR + account_settings.ACCOUNT_MULT_TWITTER)

    def test_multi_from_old_and_remove(self):
        profile = self.jerome.get_profile()
        profile.account_type = account_settings.ACCOUNT_TYPE_FACEBOOK
        profile.save()
        profile.add_account_type(account_settings.ACCOUNT_MULT_TWITTER)
        self.assertEquals(profile.account_type, account_settings.ACCOUNT_MULT_FACEBOOK + account_settings.ACCOUNT_TYPE_SEPARATOR + account_settings.ACCOUNT_MULT_TWITTER)

        profile.remove_account_type(account_settings.ACCOUNT_MULT_FACEBOOK)
        self.assertEquals(profile.account_type, account_settings.ACCOUNT_MULT_TWITTER)

    def test_add_remove_account(self):
        profile = self.jerome.get_profile()
        profile.add_account_type(account_settings.ACCOUNT_MULT_YASOUND, commit=True)

        self.assertFalse(profile.facebook_enabled)
        self.assertTrue(profile.yasound_enabled)

        # add facebook account
        profile.add_facebook_account(uid='1460646148',
                                     token='BAAENXOrG1O8BAFrSfnZCW6ZBeDPI77iwxuVV4pyerdxAZC6p0UmWH2u4OzIGhsHVH7AolQYcC5IQbqCiDzrF0CNtNbMaHrbdgVv8qWjX8LRRxhlb4E4',
                                     username='toto',
                                     email='jerome@blondon.fr',
                                     expiration_date='now')

        self.assertTrue(profile.facebook_enabled)
        self.assertTrue(profile.yasound_enabled)

        # remove it
        profile.remove_facebook_account()

        self.assertFalse(profile.facebook_enabled)
        self.assertTrue(profile.yasound_enabled)

        # trying to remove yasound account, last account so it is impossible
        res, message = profile.remove_yasound_account()
        self.assertFalse(res)

        self.assertFalse(profile.facebook_enabled)
        self.assertTrue(profile.yasound_enabled)

        # let's test the yasound removal
        res, _message = profile.add_facebook_account(uid='1460646148',
                                     token='BAAENXOrG1O8BAFrSfnZCW6ZBeDPI77iwxuVV4pyerdxAZC6p0UmWH2u4OzIGhsHVH7AolQYcC5IQbqCiDzrF0CNtNbMaHrbdgVv8qWjX8LRRxhlb4E4',
                                     username='toto',
                                     email='jerome@blondon.fr',
                                     expiration_date='now')
        if res == False:
            # sometimes, facebook is unavailable
            print _message

        res, message = profile.remove_yasound_account()
        self.assertTrue(res)
        res, message = profile.remove_facebook_account()
        self.assertFalse(res)

        self.assertTrue(profile.facebook_enabled)
        self.assertFalse(profile.yasound_enabled)

        # remove yasound account
        res, message = profile.remove_yasound_account()
        self.assertTrue(res)

        self.jerome.email = 'jbl@yasound.com'
        self.jerome.save()

        # re-add with same address
        res, message = profile.add_yasound_account('jbl@yasound.com', 'password')
        self.assertTrue(res)

        # re-add facebook
        # let's test the yasound removal
        profile.add_facebook_account(uid='1460646148',
                                     token='BAAENXOrG1O8BAFrSfnZCW6ZBeDPI77iwxuVV4pyerdxAZC6p0UmWH2u4OzIGhsHVH7AolQYcC5IQbqCiDzrF0CNtNbMaHrbdgVv8qWjX8LRRxhlb4E4',
                                     username='toto',
                                     email='jerome@blondon.fr',
                                     expiration_date='now')
        self.assertTrue(profile.facebook_enabled)

        res, _message = profile.add_facebook_account(uid='1460646148',
                                     token='BAAENXOrG1O8BAFrSfnZCW6ZBeDPI77iwxuVV4pyerdxAZC6p0UmWH2u4OzIGhsHVH7AolQYcC5IQbqCiDzrF0CNtNbMaHrbdgVv8qWjX8LRRxhlb4E4',
                                     username='toto',
                                     email='jerome@blondon.fr',
                                     expiration_date='now')
        self.assertTrue(res)
        self.assertTrue(profile.facebook_enabled)

    def test_is_multi_account(self):
        # only one account
        profile = self.jerome.get_profile()
        self.assertFalse(profile.is_multi_account)
        profile.add_account_type(account_settings.ACCOUNT_MULT_YASOUND, commit=True)

        self.assertFalse(profile.is_multi_account)

        # add facebook account
        profile.add_account_type(account_settings.ACCOUNT_MULT_FACEBOOK)
        self.assertTrue(profile.is_multi_account)

        # remove it
        profile.remove_facebook_account()
        self.assertFalse(profile.is_multi_account)

        # re-add it
        profile.add_account_type(account_settings.ACCOUNT_MULT_FACEBOOK)

        self.assertTrue(profile.is_multi_account)

        # re-remove
        res, message = profile.remove_yasound_account()
        self.assertFalse(profile.is_multi_account)

        # add twitter
        profile.add_account_type(account_settings.ACCOUNT_MULT_TWITTER)
        self.assertTrue(profile.is_multi_account)

        # add facebook
        profile.add_account_type(account_settings.ACCOUNT_MULT_FACEBOOK)
        self.assertTrue(profile.is_multi_account)

        # remove twitter
        profile.remove_twitter_account()

        self.assertFalse(profile.is_multi_account)

        # re-add yasound
        profile.add_account_type(account_settings.ACCOUNT_MULT_YASOUND)
        self.assertTrue(profile.is_multi_account)

        # remove facebook
        profile.remove_facebook_account()
        self.assertFalse(profile.is_multi_account)

    def test_remove_with_spaces(self):
        profile = self.jerome.get_profile()
        profile.account_type = 'YA, FB, TW'
        profile.save()

        self.assertTrue(profile.facebook_enabled)
        self.assertTrue(profile.twitter_enabled)
        self.assertTrue(profile.yasound_enabled)

        profile.remove_facebook_account()
        self.assertFalse(profile.facebook_enabled)
        self.assertTrue(profile.twitter_enabled)
        self.assertTrue(profile.yasound_enabled)

        profile.remove_twitter_account()
        self.assertFalse(profile.twitter_enabled)
        self.assertTrue(profile.yasound_enabled)

class TestFacebook(TestCase):
    def setUp(self):
        erase_index()

        # jbl
        jerome = User(email="jbl@yasound.com", username="jerome", is_superuser=False, is_staff=False)
        jerome.set_password('jerome')
        jerome.save()
        self.assertEqual(jerome.get_profile(), UserProfile.objects.get(id=1))

        profile = jerome.get_profile()
        profile.account_type = account_settings.ACCOUNT_TYPE_FACEBOOK
        profile.facebook_uid = '1460646148'
        profile.facebook_token = 'BAAENXOrG1O8BAFrSfnZCW6ZBeDPI77iwxuVV4pyerdxAZC6p0UmWH2u4OzIGhsHVH7AolQYcC5IQbqCiDzrF0CNtNbMaHrbdgVv8qWjX8LRRxhlb4E4'

        profile.save()

        # seb
        seb = User(email="seb@yasound.com", username="seb", is_superuser=False, is_staff=False)
        seb.set_password('seb')
        seb.save()
        self.assertEqual(seb.get_profile(), UserProfile.objects.get(id=2))

        profile = seb.get_profile()
        profile.account_type = account_settings.ACCOUNT_TYPE_FACEBOOK
        profile.facebook_uid = '1060354026'
        profile.save()

        self.jerome = jerome
        self.seb = seb

    def test_scan_friends(self):
        self.assertFalse(self.seb in self.jerome.get_profile().friends.all())
        self.assertFalse(self.jerome in self.seb.get_profile().friends.all())

        self.jerome.get_profile().scan_friends()

        self.assertTrue(self.seb in self.jerome.get_profile().friends.all())
        self.assertTrue(self.jerome in self.seb.get_profile().friends.all())

    def test_scan_task(self):
        task.scan_friends_task()
        self.assertGreater(cache.get('total_friend_count'), 20)
        self.assertEquals(cache.get('total_yasound_friend_count'), 1)

    def test_facebook_update(self):
        json = """
{
"object": "user",
"entry":
[
    {
        "uid": 1335845740,
        "changed_fields":
        [
            "name",
            "picture"
        ],
       "time": 232323
    },
    {
        "uid": 1234,
        "changed_fields":
        [
            "friends"
        ],
       "time": 232325
    }
]
}
"""
        self.client.post(reverse('facebook_update'), json, content_type='application/json')

        json = """
{
"object": "user",
"entry":
    {
        "uid": 1335845740,
        "changed_fields":
        [
            "name",
            "picture"
        ],
       "time": 232323
    }
}
"""
        self.client.post(reverse('facebook_update'), json, content_type='application/json')

        json = """
[{
"object": "user",
"entry":
    {
        "uid": 1335845740,
        "changed_fields":
        [
            "name",
            "picture"
        ],
       "time": 232323
    }
}]
"""
        self.client.post(reverse('facebook_update'), json, content_type='application/json')

        json = """
[{
"object": "user",
"entry":
    {
        "uid": 1460646148,
        "changed_fields":
        [
            "name",
            "picture"
        ],
       "time": 232323
    }
}]
"""
        self.client.post(reverse('facebook_update'), json, content_type='application/json')


class TestCurrentRadio(TestCase):
    def setUp(self):
        # jbl
        user = User(email="jbl@yasound.com", username="jerome", is_superuser=False, is_staff=False)
        user.set_password('jerome')
        user.save()
        self.user = user

    def test_current_radio(self):
        user_profile = self.user.get_profile()
        owned_radio = user_profile.own_radio
        self.assertIsNone(owned_radio)

        owned_radio = Radio.objects.create(creator=self.user)

        playlist = yabase_tests_utils.generate_playlist()
        playlist.radio = owned_radio
        playlist.save()
        owned_radio.ready = True
        owned_radio.save()
        self.assertTrue(owned_radio.is_valid)

        self.assertIsNone(user_profile.current_radio)

        RadioUser.objects.create(user=self.user, listening=True, radio=owned_radio)

        self.assertEquals(user_profile.listened_radio, owned_radio)
        self.assertEquals(user_profile.current_radio, owned_radio)

        RadioUser.objects.filter(user=self.user).update(listening=False)
        self.assertIsNone(user_profile.listened_radio)
        self.assertIsNone(user_profile.current_radio)

        RadioUser.objects.filter(user=self.user).update(connected=True)
        self.assertEquals(user_profile.connected_radio, owned_radio)
        self.assertEquals(user_profile.current_radio, owned_radio)


class TestDevice(TestCase):
    def setUp(self):
        erase_index()

    def test_ios_token_creation(self):
        user = User(email="test@yasound.com", username="test", is_superuser=False, is_staff=False)
        user.set_password('test')
        user.save()

        uuid = 'UUID9876543210'
        ios_token = 'TOKEN0123456789'
        ios_token_type = account_settings.IOS_TOKEN_TYPE_SANDBOX
        app_id = yabase_settings.IPHONE_DEFAULT_APPLICATION_IDENTIFIER

        Device.objects.store_ios_token(user, device_uuid=uuid, device_token_type=ios_token_type, device_token=ios_token, app_identifier=app_id)
        self.assertEquals(Device.objects.count(), 1)

    def test_ios_token_save(self):
        user = User(email="test@yasound.com", username="test", is_superuser=False, is_staff=False)
        user.set_password('test')
        user.save()

        uuid = 'UUID9876543210'
        ios_token = 'TOKEN0123456789'
        ios_token_type = account_settings.IOS_TOKEN_TYPE_SANDBOX
        app_id = yabase_settings.IPHONE_DEFAULT_APPLICATION_IDENTIFIER

        Device.objects.store_ios_token(user, device_uuid=uuid, device_token_type=ios_token_type, device_token=ios_token, app_identifier=app_id)

        # save again
        Device.objects.store_ios_token(user, device_uuid=uuid, device_token_type=ios_token_type, device_token=ios_token, app_identifier=app_id)

        # must contain only one device
        self.assertEquals(Device.objects.count(), 1)

    def test_ios_token_sandbox_production(self):
        user = User(email="test@yasound.com", username="test", is_superuser=False, is_staff=False)
        user.set_password('test')
        user.save()

        uuid = 'UUID9876543210'

        ios_token_sandbox = 'SANDBOX_0123456789'
        ios_token_prod = 'PRODUCTION_0123456789'
        app_id = yabase_settings.IPHONE_DEFAULT_APPLICATION_IDENTIFIER

        Device.objects.store_ios_token(user, device_uuid=uuid, device_token_type=account_settings.IOS_TOKEN_TYPE_SANDBOX, device_token=ios_token_sandbox, app_identifier=app_id)
        Device.objects.store_ios_token(user, device_uuid=uuid, device_token_type=account_settings.IOS_TOKEN_TYPE_PRODUCTION, device_token=ios_token_prod, app_identifier=app_id)
        self.assertEquals(Device.objects.filter(user=user, uuid=uuid).count(), 2)
        self.assertEquals(Device.objects.filter(user=user, uuid=uuid, ios_token_type=account_settings.IOS_TOKEN_TYPE_SANDBOX).count(), 1)
        self.assertEquals(Device.objects.filter(user=user, uuid=uuid, ios_token_type=account_settings.IOS_TOKEN_TYPE_PRODUCTION).count(), 1)


class TestApi(TestCase):
    def setUp(self):
        user = User(email="test@yasound.com", username="test", is_superuser=True, is_staff=True)
        user.set_password('test')
        user.save()
        self.client.login(username="test", password="test")
        self.user = user
        self.key = ApiKey.objects.get(user=self.user).key
        self.username = self.user.username

    def testTopLimitation(self):
        url = reverse('api_dispatch_list', kwargs={'resource_name': 'popular_user', 'api_name': 'v1', })
        res = self.client.get(url, {'api_key': self.key, 'username': self.username})
        self.assertEquals(res.status_code, 200)
        data = res.content
        decoded_data = json.loads(data)
        meta = decoded_data['meta']
        self.assertEquals(meta['total_count'], User.objects.all().count())

    def test_decorator_limit_version(self):
        url = reverse('account.views.invite_ios_contacts')
        url = url + '/?api_key=%s&username=%s' % (self.key, self.username)
        data = []
        json_data = json.dumps(data)
        res = self.client.post(url, json_data, content_type="application/json")
        self.assertEquals(res.status_code, 200)

        url = url + '&app_version=2.0.0'
        res = self.client.post(url, json_data, content_type="application/json")
        self.assertEquals(res.status_code, 403)

class TestFacebookSharePrefs(TestCase):
    def setUp(self):
        erase_index()

        user = User(email="test@yasound.com", username="test", is_superuser=True, is_staff=True)
        user.set_password('test')
        user.save()
        self.user = user
        self.key = ApiKey.objects.get(user=self.user).key
        self.username = self.user.username

    def test_facebook_share_prefs(self):
        profile = self.user.userprofile
        share_listen = profile.notifications_preferences.fb_share_listen
        share_like = profile.notifications_preferences.fb_share_like_song
        share_message = profile.notifications_preferences.fb_share_post_message
        share_activity = profile.notifications_preferences.fb_share_animator_activity

        share_like = not share_like
        share_message = not share_message

        pref_dict = {
                     'fb_share_listen': share_listen,
                     'fb_share_like_song': share_like,
                     'fb_share_post_message': share_message,
                     'fb_share_animator_activity': share_activity,
                     }
        profile.set_facebook_share_preferences(pref_dict)

        d = profile.facebook_share_preferences()

        self.assertEqual(d, pref_dict)
        self.assertEqual(share_listen, profile.notifications_preferences.fb_share_listen)
        self.assertEqual(share_like, profile.notifications_preferences.fb_share_like_song)
        self.assertEqual(share_message, profile.notifications_preferences.fb_share_post_message)
        self.assertEqual(share_activity, profile.notifications_preferences.fb_share_animator_activity)

    def test_security(self):
        pref_dict = {
                     'fb_share_listen': True,
                     'fb_share_like_song': True,
                     'fb_share_post_message': True,
                     'fb_share_animator_activity': True,
                     }

        res = self.client.get('/api/v1/facebook_share_preferences/')
        self.assertEquals(res.status_code, 401)

        res = self.client.put('/api/v1/facebook_share_preferences/?api_key=%s&username=%s' % (self.key, self.username), pref_dict, content_type='application/json')
        self.assertEquals(res.status_code, 405)

        res = self.client.delete('/api/v1/facebook_share_preferences/?api_key=%s&username=%s' % (self.key, self.username))
        self.assertEquals(res.status_code, 405)

        res = self.client.post('/api/v1/facebook_share_preferences/?api_key=%s&username=%s' % (self.key, self.username), pref_dict, content_type='application/json')
        self.assertEquals(res.status_code, 405)

        res = self.client.get('/api/v1/facebook_share_preferences/', {'api_key': self.key, 'username': self.username})
        self.assertEquals(res.status_code, 200)

        res = self.client.post('/api/v1/set_facebook_share_preferences/', pref_dict)
        self.assertEquals(res.status_code, 401)

        res = self.client.put('/api/v1/set_facebook_share_preferences/?api_key=%s&username=%s' % (self.key, self.username), pref_dict, content_type='application/json')
        self.assertEquals(res.status_code, 405)

        res = self.client.delete('/api/v1/set_facebook_share_preferences/?api_key=%s&username=%s' % (self.key, self.username))
        self.assertEquals(res.status_code, 405)

        res = self.client.get('/api/v1/set_facebook_share_preferences/?api_key=%s&username=%s' % (self.key, self.username))
        self.assertEquals(res.status_code, 405)

        res = self.client.post('/api/v1/set_facebook_share_preferences/?api_key=%s&username=%s' % (self.key, self.username), json.dumps(pref_dict), content_type='application/json')
        self.assertEquals(res.status_code, 200)

    def test_get_view(self):
        profile = self.user.userprofile
        res = self.client.get('/api/v1/facebook_share_preferences/', {'api_key': self.key, 'username': self.username})
        self.assertEquals(res.status_code, 200)
        prefs = json.loads(res.content)
        self.assertEqual(prefs, profile.facebook_share_preferences())

    def test_post_view(self):
        profile = self.user.userprofile
        pref_dict = profile.facebook_share_preferences()

        share_listen = pref_dict['fb_share_listen']
        pref_dict['fb_share_listen'] = not share_listen

        res = self.client.post('/api/v1/set_facebook_share_preferences/?api_key=%s&username=%s' % (self.key, self.username), json.dumps(pref_dict), content_type='application/json')
        self.assertEquals(res.status_code, 200)

        profile = UserProfile.objects.get(id=profile.id)
        prefs_now = profile.facebook_share_preferences()
        self.assertEquals(pref_dict, prefs_now)


class TestNotifications(TestCase):
    def setUp(self):
        erase_index()

        nm = NotificationsManager()
        nm.notifications.drop()

    def test_friend_is_online(self):
        nm = NotificationsManager()
        user1 = User.objects.create(email="user1@yasound.com", username="user1")
        user2 = User.objects.create(email="user2@yasound.com", username="user2")

        user1.get_profile().add_friend(user2)

        user2.get_profile().my_friend_is_online(user1.get_profile())

        notifications = nm.notifications.find({'type': yamessage_settings.TYPE_NOTIF_FRIEND_ONLINE}).sort([('date', DESCENDING)])
        self.assertEquals(notifications.count(), 1)

        user2.get_profile().my_friend_is_online(user1.get_profile())

        notifications = nm.notifications.find({'type': yamessage_settings.TYPE_NOTIF_FRIEND_ONLINE}).sort([('date', DESCENDING)])
        self.assertEquals(notifications.count(), 1)

        nm.notifications.drop()

        notifications = nm.notifications.find({'type': yamessage_settings.TYPE_NOTIF_FRIEND_ONLINE}).sort([('date', DESCENDING)])
        self.assertEquals(notifications.count(), 0)

        user2.get_profile().my_friend_is_online(user1.get_profile())
        notifications = nm.notifications.find({'type': yamessage_settings.TYPE_NOTIF_FRIEND_ONLINE}).sort([('date', DESCENDING)])
        self.assertEquals(notifications.count(), 1)

        notification = notifications[0]
        notification['date'] = datetime.datetime(2007, 01, 01, 0, 0, 0)
        nm.update_notification(notification)

        user2.get_profile().my_friend_is_online(user1.get_profile())
        notifications = nm.notifications.find({'type': yamessage_settings.TYPE_NOTIF_FRIEND_ONLINE}).sort([('date', DESCENDING)])
        self.assertEquals(notifications.count(), 2)

        radio = Radio.objects.create(name='foo', creator=user1)
        default_playlist, _created = radio.get_or_create_default_playlist()
        sm = SongMetadata.objects.create(name='foo')
        song = SongInstance.objects.create(playlist=default_playlist, metadata=sm)
        user2.get_profile().song_liked_in_my_radio(user1.get_profile(), radio, song)

        wall_message = WallEvent.objects.create(radio=radio, user=user1)
        user2.get_profile().message_posted_in_my_radio(wall_message)
        user2.get_profile().my_radio_added_in_favorites(user1.get_profile(), radio)
        user2.get_profile().my_radio_shared(user1.get_profile(), radio)
        user2.get_profile().my_friend_created_radio(user1.get_profile(), radio)
        user2.get_profile().message_from_yasound('hello, world')

class TestWebPreferences(TestCase):
    def setUp(self):
        erase_index()
        ua = UserAdditionalInfosManager()
        ua.erase_informations()

    def test_preferences(self):
        user1 = User.objects.create(email="user1@yasound.com", username="user1")
        profile1 = user1.get_profile()
        preferences = profile1.web_preferences()
        self.assertEquals(preferences, {})

        profile1.set_web_preferences('pref1', True)
        preferences = profile1.web_preferences()
        self.assertEquals(len(preferences), 1)
        self.assertTrue(preferences['pref1'])

        profile1.set_web_preferences('pref1', False)
        preferences = profile1.web_preferences()
        self.assertEquals(len(preferences), 1)
        self.assertFalse(preferences['pref1'])

        profile1.set_web_preferences('pref2', 42)
        preferences = profile1.web_preferences()
        self.assertEquals(len(preferences), 2)
        self.assertFalse(preferences['pref1'])
        self.assertEquals(preferences['pref2'], 42)


class TestInvitationsManager(TestCase):
    def setUp(self):
        erase_index()
        ia = InvitationsManager()
        ia.erase_informations()

    def test_add(self):
        user1 = User.objects.create(email="user1@yasound.com", username="user1")
        profile1 = user1.get_profile()

        ia = InvitationsManager()

        self.assertFalse(ia.has_invitation(profile1.user.id, InvitationsManager.TYPE_FACEBOOK, 42))

        ia.add_invitations(profile1.user.id, InvitationsManager.TYPE_FACEBOOK, [42, 43, 44])

        self.assertTrue(ia.has_invitation(profile1.user.id, InvitationsManager.TYPE_FACEBOOK, 42))
        self.assertTrue(ia.has_invitation(profile1.user.id, InvitationsManager.TYPE_FACEBOOK, 43))
        self.assertTrue(ia.has_invitation(profile1.user.id, InvitationsManager.TYPE_FACEBOOK, 44))
        self.assertFalse(ia.has_invitation(profile1.user.id, InvitationsManager.TYPE_FACEBOOK, 45))

        ia.add_invitations(profile1.user.id, InvitationsManager.TYPE_EMAIL, ['jerome@blondon.fr'])
        self.assertFalse(ia.has_invitation(profile1.user.id, InvitationsManager.TYPE_FACEBOOK, 'jerome@blondon.fr'))
        self.assertTrue(ia.has_invitation(profile1.user.id, InvitationsManager.TYPE_EMAIL, 'jerome@blondon.fr'))

        ia.add_invitations(profile1.user.id, InvitationsManager.TYPE_TWITTER, ['jbl2024'])
        self.assertFalse(ia.has_invitation(profile1.user.id, InvitationsManager.TYPE_FACEBOOK, 'jbl2024'))
        self.assertFalse(ia.has_invitation(profile1.user.id, InvitationsManager.TYPE_EMAIL, 'jbl2024'))
        self.assertTrue(ia.has_invitation(profile1.user.id, InvitationsManager.TYPE_TWITTER, 'jbl2024'))

        ia.remove_invitation(profile1.user.id, InvitationsManager.TYPE_TWITTER, 'jbl2024')
        self.assertFalse(ia.has_invitation(profile1.user.id, InvitationsManager.TYPE_FACEBOOK, 'jbl2024'))
        self.assertFalse(ia.has_invitation(profile1.user.id, InvitationsManager.TYPE_EMAIL, 'jbl2024'))
        self.assertFalse(ia.has_invitation(profile1.user.id, InvitationsManager.TYPE_TWITTER, 'jbl2024'))

        ia.remove_invitation(profile1.user.id, InvitationsManager.TYPE_EMAIL, 'jerome@blondon.fr')
        self.assertFalse(ia.has_invitation(profile1.user.id, InvitationsManager.TYPE_FACEBOOK, 'jerome@blondon.fr'))
        self.assertFalse(ia.has_invitation(profile1.user.id, InvitationsManager.TYPE_EMAIL, 'jerome@blondon.fr'))

        users_id = ia.find_invitation_providers(InvitationsManager.TYPE_FACEBOOK, 42)
        self.assertEquals(users_id[0].get('db_id'), user1.id)

class TestIphoneVersion(TestCase):
    def setUp(self):
        pass

    def test_versions(self):
        request = RequestFactory().get('/?username=100001622138259@facebook&api_key=d6c5200968defb0503a0ecb3ac3111619a6173ed&app_id=com.yasound.yasound&app_version=2.0.38')
        self.assertFalse(is_iphone_version_1(request))
        self.assertTrue(is_iphone_version_2(request))

        request = RequestFactory().get('/?username=100001622138259@facebook&api_key=d6c5200968defb0503a0ecb3ac3111619a6173ed&app_id=com.yasound.yasound&app_version=1.0.38')
        self.assertTrue(is_iphone_version_1(request))
        self.assertFalse(is_iphone_version_2(request))


class TestInvitationViews(TestCase):
    def setUp(self):
        user = User(email="test@yasound.com", username="test")
        user.set_password('test')
        user.save()
        self.client.login(username="test", password="test")
        self.user = user
        self.key = ApiKey.objects.get(user=self.user).key
        self.username = self.user.username

    def test_invite_ios_contacts(self):
        data = [
            {
                'firstName': 'joe',
                'lastName': 'dalton',
                'emails': ['jbl@yasound.com', 'jerome@yasound.com']
            }
        ]
        json_data = json.dumps(data)
        r = self.client.post(reverse('account.views.invite_ios_contacts'), json_data, content_type="application/json")
        self.assertEquals(r.status_code, 200)

class TestAnonymous(TestCase):
    def setUp(self):
        manager = AnonymousManager()
        manager.erase_informations()
        pass

    def test_upsert(self):
        manager = AnonymousManager()
        manager.upsert_anonymous('id1', 'uuid1')

        # radio with no users
        anons = manager.anonymous_for_radio('uuid')
        self.assertEquals(anons.count(), 0)

        # radio with 1 user
        anons = manager.anonymous_for_radio('uuid1')
        self.assertEquals(anons.count(), 1)
        self.assertEquals(anons[0].get('anonymous_id'), 'id1')

        # duplicate insert in same radio
        manager.upsert_anonymous('id1', 'uuid1')
        anons = manager.anonymous_for_radio('uuid1')
        self.assertEquals(anons.count(), 1)

        # add id2 to uuid1
        manager.upsert_anonymous('id2', 'uuid1')
        anons = manager.anonymous_for_radio('uuid1')
        self.assertEquals(anons.count(), 2)

        # add id1 to uuid2
        manager.upsert_anonymous('id1', 'uuid2')
        anons = manager.anonymous_for_radio('uuid2')
        self.assertEquals(anons.count(), 1)
        self.assertEquals(anons[0].get('anonymous_id'), 'id1')

        anons = manager.anonymous_for_radio('uuid1')
        self.assertEquals(anons.count(), 1)
        self.assertEquals(anons[0].get('anonymous_id'), 'id2')

    def test_remove_inactive_users(self):
        manager = AnonymousManager()
        manager.upsert_anonymous('id1', 'uuid1')
        manager.upsert_anonymous('id2', 'uuid1')

        # radio with 2 user
        anons = manager.anonymous_for_radio('uuid1')
        self.assertEquals(anons.count(), 2)

        manager.remove_inactive_users()

        anons = manager.anonymous_for_radio('uuid1')
        self.assertEquals(anons.count(), 2)

        now = datetime.datetime.now()
        expired_date = now + relativedelta(seconds=-AnonymousManager.ANONYMOUS_TTL-1)

        doc = {
            'anonymous_id': 'id1',
            'radio_uuid': 'uuid1',
            'updated': expired_date
        }
        manager.collection.update({'anonymous_id': 'id1'}, {'$set': doc }, upsert=True, safe=True)

        manager.remove_inactive_users()

        anons = manager.anonymous_for_radio('uuid1')
        self.assertEquals(anons.count(), 1)
        self.assertEquals(anons[0].get('anonymous_id'), 'id2')

