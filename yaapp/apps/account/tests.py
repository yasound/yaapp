from account.models import UserProfile
from django.contrib.auth.models import User
from django.test import TestCase

from yasearch.indexer import erase_index

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
                
        