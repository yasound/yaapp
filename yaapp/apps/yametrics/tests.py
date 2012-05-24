from django.contrib.auth.models import User
from django.test import TestCase
from models import GlobalMetricsManager
from yabase import tests_utils as yabase_tests_utils
from yabase.models import Radio, SongMetadata
from yametrics.models import TopMissingSongsManager, RadioMetricsManager, \
    TimedMetricsManager, UserMetricsManager
from yametrics.task import async_activity, update_activities
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

class TestTimedMetrics(TestCase):
    def setUp(self):
        user = User(email="test@yasound.com", username="test", is_superuser=False, is_staff=False)
        user.set_password('test')
        user.save()
        self.client.login(username="test", password="test")
        self.user = user   
        tm = TimedMetricsManager()
        tm.erase_metrics()
        um = UserMetricsManager()
        um.erase_metrics()
        
    def test_slots(self):
        tm = TimedMetricsManager()
        self.assertEquals(tm.slot(0), tm.SLOT_24H)
        self.assertEquals(tm.slot(1), tm.SLOT_3D)
        self.assertEquals(tm.slot(2), tm.SLOT_3D)
        self.assertEquals(tm.slot(3), tm.SLOT_3D)
        
        self.assertEquals(tm.slot(4), tm.SLOT_7D)
        self.assertEquals(tm.slot(5), tm.SLOT_7D)
        self.assertEquals(tm.slot(7), tm.SLOT_7D)

        self.assertEquals(tm.slot(8), tm.SLOT_15D)
        self.assertEquals(tm.slot(15), tm.SLOT_15D)
 
        self.assertEquals(tm.slot(16), tm.SLOT_30D)
        self.assertEquals(tm.slot(20), tm.SLOT_30D)

        self.assertEquals(tm.slot(31), tm.SLOT_90D)
        self.assertEquals(tm.slot(40), tm.SLOT_90D)

        self.assertEquals(tm.slot(160), tm.SLOT_90D_MORE)
        
    def test_async_animator_activity(self):
        async_activity(self.user.id, 'animator_activity')
        
        tm = TimedMetricsManager()
        docs = tm.collection.find()
        self.assertEquals(docs.count(), 1)
        self.assertEquals(docs[0]['animator_activity'], 1)

        async_activity(self.user.id, 'animator_activity')

        um = UserMetricsManager()
        user_doc = um.get_doc(self.user.id)
        self.assertEquals(user_doc['animator_activity'], 1)
        self.assertEquals(user_doc['last_animator_activity_slot'], tm.SLOT_24H)

        now = datetime.datetime.now()
        past = now + datetime.timedelta(days=-3)
        um.set_value(self.user.id, 'last_animator_activity_date', past)

        update_activities(['animator_activity'])
        docs = tm.collection.find()
        self.assertEquals(docs.count(), 2)
        for doc in docs:
            ttype = doc['type']
            if ttype == tm.SLOT_24H:
                self.assertEquals(doc['animator_activity'], 0)
            else:
                self.assertEquals(ttype, tm.SLOT_3D)
                self.assertEquals(doc['animator_activity'], 1)
                