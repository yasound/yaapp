from account.models import UserProfile
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.test import TestCase
from yasearch.indexer import erase_index
import settings as account_settings
import task

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
        self.assertEquals(cache.get('total_friend_count'), 16)
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
