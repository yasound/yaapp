from account.models import UserProfile, Device
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils import simplejson as json
from tastypie.models import ApiKey
from yabase import tests_utils as yabase_tests_utils
from yabase.models import RadioUser
from yasearch.indexer import erase_index
import settings as account_settings
import task
import yabase.settings as yabase_settings
from Carbon.Aliases import true

class TestProfile(TestCase):
    def setUp(self):
        erase_index()
        
    def test_profile_creation(self):
        user = User(email="test@yasound.com", username="test", is_superuser=False, is_staff=False)
        user.set_password('test')
        user.save()
        self.assertEqual(user.get_profile(), UserProfile.objects.get(id=1))

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
        self.assertEquals(profile.account_type, account_settings.ACCOUNT_MULT_FACEBOOK + account_settings.ACCOUNT_TYPE_SEPARATOR+account_settings.ACCOUNT_MULT_TWITTER)
        
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
        self.assertEquals(profile.account_type, account_settings.ACCOUNT_MULT_FACEBOOK + account_settings.ACCOUNT_TYPE_SEPARATOR+account_settings.ACCOUNT_MULT_TWITTER)
        
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
        self.assertEquals(profile.account_type, account_settings.ACCOUNT_MULT_FACEBOOK + account_settings.ACCOUNT_TYPE_SEPARATOR+account_settings.ACCOUNT_MULT_TWITTER)
        

    def test_multi_from_old_and_remove(self):
        profile = self.jerome.get_profile()
        profile.account_type = account_settings.ACCOUNT_TYPE_FACEBOOK
        profile.save()
        profile.add_account_type(account_settings.ACCOUNT_MULT_TWITTER)
        self.assertEquals(profile.account_type, account_settings.ACCOUNT_MULT_FACEBOOK + account_settings.ACCOUNT_TYPE_SEPARATOR+account_settings.ACCOUNT_MULT_TWITTER)

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

        res, _message =  profile.add_facebook_account(uid='1460646148',
                                     token='BAAENXOrG1O8BAFrSfnZCW6ZBeDPI77iwxuVV4pyerdxAZC6p0UmWH2u4OzIGhsHVH7AolQYcC5IQbqCiDzrF0CNtNbMaHrbdgVv8qWjX8LRRxhlb4E4',
                                     username='toto',
                                     email='jerome@blondon.fr',
                                     expiration_date='now')
        self.assertTrue(res)
        self.assertTrue(profile.facebook_enabled)
        
        
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
        self.assertEquals(owned_radio.id, 1)
        
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
        url = reverse('api_dispatch_list', kwargs={'resource_name': 'popular_user', 'api_name': 'v1',})
        res = self.client.get(url,{'api_key': self.key, 'username': self.username})
        self.assertEquals(res.status_code, 200)
        data = res.content
        decoded_data = json.loads(data)
        meta = decoded_data['meta']
        self.assertEquals(meta['total_count'], User.objects.all().count())
   

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
        
        res = self.client.get('/api/v1/facebook_share_preferences/',{'api_key': self.key, 'username': self.username})
        self.assertEquals(res.status_code, 200)
        
        
        res = self.client.post('/api/v1/facebook_share_preferences/', pref_dict)
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
        res = self.client.get('/api/v1/facebook_share_preferences/',{'api_key': self.key, 'username': self.username})
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
        
        
        
              
        
        