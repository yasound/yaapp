from django.contrib.auth.models import User
from django.test import TestCase
from models import Country, GeoFeature
import utils as yageoperm_utils
import settings as yageoperm_settings

class TestFeatures(TestCase):
    
    def setUp(self):
        user = User(email="test@yasound.com", username="test", is_superuser=False, is_staff=False)
        user.set_password('test')
        user.save()
        self.user = user
        self.client.login(username="test", password="test")
        
        
    def test_can_login(self):
        self.assertFalse(yageoperm_utils.can_login(user=self.user, country='FR'))
        
        self.user.is_superuser = True
        self.user.save()

        self.assertTrue(yageoperm_utils.can_login(user=self.user, country='FR'))

        self.user.is_superuser = False
        self.user.save()
        
        country = Country.objects.create(code='FR', name='France')
        GeoFeature.objects.create(country=country, feature=yageoperm_settings.FEATURE_LOGIN)
        self.assertTrue(yageoperm_utils.can_login(user=self.user, country='FR'))
        self.assertFalse(yageoperm_utils.can_login(user=self.user, country='UK'))

    def test_can_create_radio(self):
        self.assertFalse(yageoperm_utils.can_create_radio(user=self.user, country='FR'))
        
        self.user.is_superuser = True
        self.user.save()

        self.assertTrue(yageoperm_utils.can_create_radio(user=self.user, country='FR'))

        self.user.is_superuser = False
        self.user.save()
        
        country = Country.objects.create(code='FR', name='France')
        GeoFeature.objects.create(country=country, feature=yageoperm_settings.FEATURE_CREATE_RADIO)
        self.assertTrue(yageoperm_utils.can_create_radio(user=self.user, country='FR'))
        self.assertFalse(yageoperm_utils.can_create_radio(user=self.user, country='UK'))
        