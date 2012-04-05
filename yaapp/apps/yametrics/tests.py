from django.contrib.auth.models import User
from django.test import TestCase
from models import MetricsManager
from yabase.models import Radio
import datetime

class TestMetricsManager(TestCase):
    def setUp(self):
        mm = MetricsManager()
        mm.erase_global_metrics()

        user = User(email="test@yasound.com", username="test", is_superuser=False, is_staff=False)
        user.set_password('test')
        user.save()
        self.client.login(username="test", password="test")
        self.user = user        
    
    def test_inc_global_value(self):
        mm = MetricsManager()
        mm.inc_global_value("val1", 10)
        mm.inc_global_value("val2", 12)
        
        now = datetime.datetime.now()
        year = now.strftime('%Y')
        month = now.strftime('%Y-%m')
        
        self.assertEquals(mm.get_metrics_for_timestamp(year)['val1'], 10)
        self.assertEquals(mm.get_metrics_for_timestamp(year)['val2'], 12)
        self.assertEquals(mm.get_metrics_for_timestamp(month)['val1'], 10)
        self.assertEquals(mm.get_metrics_for_timestamp(month)['val2'], 12)
        
        mm.inc_global_value("val1", 10)
        mm.inc_global_value("val2", 12)

        self.assertEquals(mm.get_metrics_for_timestamp(year)['val1'], 20)
        self.assertEquals(mm.get_metrics_for_timestamp(year)['val2'], 24)
        self.assertEquals(mm.get_metrics_for_timestamp(month)['val1'], 20)
        self.assertEquals(mm.get_metrics_for_timestamp(month)['val2'], 24)
        
    def test_sample_metrics(self):
        mm = MetricsManager()
        now = datetime.datetime.now()
        year = now.strftime('%Y')
        self.assertEquals(mm.get_metrics_for_timestamp(year)['new_radios'], 1)

        Radio(name='pizza', ready=True, creator=self.user).save()
        Radio(name='ben', ready=True, creator=self.user).save()
        
        self.assertEquals(mm.get_metrics_for_timestamp(year)['new_radios'], 3)
        self.assertEquals(mm.get_metrics_for_timestamp(year)['new_users'], 1)
        