from django.contrib.auth.models import User
from django.test import TestCase
from models import GlobalMetricsManager
from yabase import tests_utils as yabase_tests_utils
from yabase.models import Radio, SongMetadata
from yametrics.models import TopMissingSongsManager, RadioMetricsManager
import datetime

class TestGlobalMetricsManager(TestCase):
    def setUp(self):
        mm = GlobalMetricsManager()
        mm.erase_global_metrics()

        user = User(email="test@yasound.com", username="test", is_superuser=False, is_staff=False)
        user.set_password('test')
        user.save()
        self.client.login(username="test", password="test")
        self.user = user        
    
    def test_inc_global_value(self):
        mm = GlobalMetricsManager()
        mm.inc_global_value("val1", 10)
        mm.inc_global_value("val2", 12)
        
        now = datetime.datetime.now()
        year = now.strftime('%Y')
        month = now.strftime('%Y-%m')
        day = now.strftime('%Y-%m-%d')
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

        mm.set_daily_value("daily_val1", 100)
        self.assertEquals(mm.get_metrics_for_timestamp(day)['daily_val1'], 100)

        mm.set_daily_value("daily_val1", 200)
        self.assertEquals(mm.get_metrics_for_timestamp(day)['daily_val1'], 200)
        
    def test_sample_metrics(self):
        mm = GlobalMetricsManager()
        now = datetime.datetime.now()
        year = now.strftime('%Y')
        self.assertEquals(mm.get_metrics_for_timestamp(year)['new_radios'], 1)

        Radio(name='pizza', ready=True, creator=self.user).save()
        Radio(name='ben', ready=True, creator=self.user).save()
        
        self.assertEquals(mm.get_metrics_for_timestamp(year)['new_radios'], 3)
        self.assertEquals(mm.get_metrics_for_timestamp(year)['new_users'], 1)
        
    def test_graph_metrics(self):
        mm = GlobalMetricsManager()
        now = datetime.datetime.now()
        timestamps = mm._generate_graph_timestamps(now)
        self.assertEquals(len(timestamps), 90)
        collection = mm.metrics_glob
        for timestamp in timestamps:
            collection.update({
                "timestamp": timestamp
            }, {
                "$set": {'key': 100}
            }, upsert=True, safe=True)

        data = mm.get_graph_metrics(['key'])
        self.assertEquals(len(data), 5)
        print data

        
        
class TestRadioMetricsManager(TestCase):
    def setUp(self):
        rm = RadioMetricsManager()
        rm.erase_metrics()

        user = User(email="test@yasound.com", username="test", is_superuser=False, is_staff=False)
        user.set_password('test')
        user.save()
        self.client.login(username="test", password="test")
        self.user = user        
    
    def test_inc_radio_value(self):
        rm = RadioMetricsManager()

        rm.inc_value(1, "val1", 10)
        rm.inc_value(1, "val2", 12)

        self.assertEquals(rm.metrics(1)['val1'], 10)
        self.assertEquals(rm.metrics(1)['val2'], 12)

        rm.inc_value(1, "val1", 10)
        rm.inc_value(1, "val2", 12)

        self.assertEquals(rm.metrics(1)['val1'], 20)
        self.assertEquals(rm.metrics(1)['val2'], 24)


        rm.inc_value(2, "val1", 10)
        rm.inc_value(2, "val2", 12)

        self.assertEquals(rm.metrics(1)['val1'], 20)
        self.assertEquals(rm.metrics(1)['val2'], 24)

        self.assertEquals(rm.metrics(2)['val1'], 10)
        self.assertEquals(rm.metrics(2)['val2'], 12)

        data = rm.filter(key='val1', id_only=True)
        self.assertEquals(data[0]['db_id'], 1)
        
class TestTopMissingSongsManager(TestCase):
    def setUp(self):
        user = User(email="test@yasound.com", username="test", is_superuser=False, is_staff=False)
        user.set_password('test')
        user.save()
        self.client.login(username="test", password="test")
        self.user = user        

    def test_values(self):
        yabase_tests_utils.generate_playlist()
        SongMetadata.objects.all().update(yasound_song_id=None)
        
        mm = TopMissingSongsManager()
        mm.calculate(100)
        docs = mm.all()
        self.assertEquals(docs.count(), SongMetadata.objects.all().count())

        mm.calculate(100)
        docs = mm.all()
        self.assertEquals(docs.count(), SongMetadata.objects.all().count())

        SongMetadata.objects.all().update(yasound_song_id=1)

        mm.calculate(100)
        docs = mm.all()
        self.assertEquals(docs.count(), 0)
