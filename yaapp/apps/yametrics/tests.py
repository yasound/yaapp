from django.contrib.auth.models import User
from django.test import TestCase
from models import GlobalMetricsManager
from yabase import tests_utils as yabase_tests_utils
from yabase.models import Radio, SongMetadata
from yametrics.models import TopMissingSongsManager, RadioMetricsManager, \
    TimedMetricsManager, UserMetricsManager, RadioPopularityManager
from yametrics.task import async_activity, update_activities
import datetime
import settings as yametrics_settings
from bson.objectid import ObjectId

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
        
    def test_daily_popularity(self):
        rm = RadioMetricsManager()

        rm.inc_value(1, "daily_popularity", 10)
        self.assertEquals(rm.metrics(1)['daily_popularity'], 10)
        
        rm.reset_daily_popularity()
        self.assertEquals(rm.metrics(1)['daily_popularity'], 0)
        
        
        
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
        async_activity(self.user.id, yametrics_settings.ACTIVITY_ANIMATOR)
        
        tm = TimedMetricsManager()
        docs = tm.collection.find()
        self.assertEquals(docs.count(), 1)
        self.assertEquals(docs[0][yametrics_settings.ACTIVITY_ANIMATOR], 1)

        async_activity(self.user.id, yametrics_settings.ACTIVITY_ANIMATOR)

        um = UserMetricsManager()
        user_doc = um.get_doc(self.user.id)
        self.assertEquals(user_doc[yametrics_settings.ACTIVITY_ANIMATOR], 1)
        self.assertEquals(user_doc['last_animator_activity_slot'], tm.SLOT_24H)

        now = datetime.datetime.now()
        past = now + datetime.timedelta(days=-3)
        um.set_value(self.user.id, 'last_animator_activity_date', past)

        update_activities()
        docs = tm.collection.find()
        self.assertEquals(docs.count(), 2)
        for doc in docs:
            ttype = doc['type']
            if ttype == tm.SLOT_24H:
                self.assertEquals(doc[yametrics_settings.ACTIVITY_ANIMATOR], 0)
            else:
                self.assertEquals(ttype, tm.SLOT_3D)
                self.assertEquals(doc[yametrics_settings.ACTIVITY_ANIMATOR], 1)

        # idempotent action
        update_activities()
        docs = tm.collection.find()
        self.assertEquals(docs.count(), 2)
        for doc in docs:
            ttype = doc['type']
            if ttype == tm.SLOT_24H:
                self.assertEquals(doc[yametrics_settings.ACTIVITY_ANIMATOR], 0)
            else:
                self.assertEquals(ttype, tm.SLOT_3D)
                self.assertEquals(doc[yametrics_settings.ACTIVITY_ANIMATOR], 1)
                
    def test_messages_stats(self):
        async_activity(self.user.id, yametrics_settings.ACTIVITY_WALL_MESSAGE, throttle=False)

        um = UserMetricsManager()
        stats = um.messages_stats()
        self.assertEquals(stats.count(), 0)
        
        um.update_messages_stats()
        
        stats = um.messages_stats()
        self.assertEquals(stats.count(), 1)
        doc = stats[0]
        self.assertEquals(doc['_id'], 1)
        self.assertEquals(doc['value'], 1)

        # fake user
        async_activity(42, yametrics_settings.ACTIVITY_WALL_MESSAGE, throttle=False)
        um.update_messages_stats()
        stats = um.messages_stats()
        self.assertEquals(stats.count(), 1)
        doc = stats[0]
        self.assertEquals(doc['_id'], 1)
        self.assertEquals(doc['value'], 2)
        
        async_activity(42, yametrics_settings.ACTIVITY_WALL_MESSAGE, throttle=False)
        um.update_messages_stats()
        stats = um.messages_stats()
        
        self.assertEquals(stats.count(), 2)
        doc = stats[0]
        self.assertEquals(doc['_id'], 1)
        self.assertEquals(doc['value'], 1)

        doc = stats[1]
        self.assertEquals(doc['_id'], 2)
        self.assertEquals(doc['value'], 1)
                
        mean = um.calculate_messages_per_user_mean()
        self.assertEquals(mean, 1.5)

    def test_likes_stats(self):
        async_activity(self.user.id, yametrics_settings.ACTIVITY_SONG_LIKE, throttle=False)

        um = UserMetricsManager()
        stats = um.likes_stats()
        self.assertEquals(stats.count(), 0)
        
        um.update_likes_stats()
        
        stats = um.likes_stats()
        self.assertEquals(stats.count(), 1)
        doc = stats[0]
        self.assertEquals(doc['_id'], 1)
        self.assertEquals(doc['value'], 1)

        # fake user
        async_activity(42, yametrics_settings.ACTIVITY_SONG_LIKE, throttle=False)
        um.update_likes_stats()
        stats = um.likes_stats()
        self.assertEquals(stats.count(), 1)
        doc = stats[0]
        self.assertEquals(doc['_id'], 1)
        self.assertEquals(doc['value'], 2)
        
        async_activity(42, yametrics_settings.ACTIVITY_SONG_LIKE, throttle=False)
        um.update_likes_stats()
        stats = um.likes_stats()
        
        self.assertEquals(stats.count(), 2)
        doc = stats[0]
        self.assertEquals(doc['_id'], 1)
        self.assertEquals(doc['value'], 1)

        doc = stats[1]
        self.assertEquals(doc['_id'], 2)
        self.assertEquals(doc['value'], 1)
                
        mean = um.calculate_likes_per_user_mean()
        self.assertEquals(mean, 1.5)        
        
        
class TestRadioPopularityManager(TestCase):
    def setUp(self):
        manager = RadioPopularityManager()
        manager.drop()
        manager.drop_settings()

        user = User(email="test@yasound.com", username="test", is_superuser=False, is_staff=False)
        user.set_password('test')
        user.save()
        self.client.login(username="test", password="test")
        self.user = user    
        
        
    def test_actions(self):
        manager = RadioPopularityManager()
        radio_id = 1 
        
        self.assertEquals(manager.radios.count(), 0)
        manager.action(radio_id, yametrics_settings.ACTIVITY_LISTEN)
        self.assertEquals(manager.radios.count(), 1)
        manager.action(radio_id, yametrics_settings.ACTIVITY_LISTEN)
        self.assertEquals(manager.radios.count(), 1)
        
        activity = manager.radios.find()[0]['activity']
        self.assertGreater(activity, 0)
        
    def test_compute_progression_cleans_useless_documents(self):
        manager = RadioPopularityManager()
        radio_id_1 = 1
        radio_id_2 = 2
        radio_id_3 = 3
        
        self.assertEquals(manager.radios.count(), 0)
        manager.action(radio_id_1, yametrics_settings.ACTIVITY_LISTEN)
        self.assertEquals(manager.radios.count(), 1)
        
        # check compute_progression removes documents without 'activity' or with 'activity' = 0
        manager.radios.insert({'db_id': radio_id_2, 'bla':123})
        self.assertEquals(manager.radios.count(), 2)
        manager.radios.insert({'db_id': radio_id_3, 'activity':0})
        self.assertEquals(manager.radios.count(), 3)
        
        manager.compute_progression()
        self.assertEquals(manager.radios.count(), 1)
        
    def test_compute_progression1(self):
        # simple case:
        #    activity is non zero
        #    last_activity exists
        manager = RadioPopularityManager()
        radio_id_1 = 1
        activity = 55
        last_activity = 20
        
        self.assertEquals(manager.radios.count(), 0)
        manager.radios.insert({'db_id': radio_id_1, 'activity':activity, 'last_activity':last_activity})
        manager.compute_progression()
        self.assertEquals(manager.radios.count(), 1)
        
        
        doc = manager.radios.find({'db_id': radio_id_1})[0]
        self.assertEquals(doc['progression'], activity - last_activity)
        
    def test_compute_progression2(self):
        # second case:
        #    activity is non zero
        #    last_activity DOES NOT exist
        manager = RadioPopularityManager()
        radio_id_1 = 1
        activity = 55
        
        self.assertEquals(manager.radios.count(), 0)
        manager.radios.insert({'db_id': radio_id_1, 'activity':activity})
        manager.compute_progression()
        self.assertEquals(manager.radios.count(), 1)
        
        
        doc = manager.radios.find({'db_id': radio_id_1})[0]
        self.assertEquals(doc['progression'], activity)
        
    def test_most_popular(self):
        manager = RadioPopularityManager()
        radio_id_1 = 1
        radio_id_2 = 2
        radio_id_3 = 3
        radio_id_4 = 4
        
        manager.action(radio_id_1, yametrics_settings.ACTIVITY_LISTEN)
        manager.action(radio_id_1, yametrics_settings.ACTIVITY_LISTEN)
        manager.action(radio_id_1, yametrics_settings.ACTIVITY_LISTEN)
        
        manager.action(radio_id_2, yametrics_settings.ACTIVITY_LISTEN)
        manager.action(radio_id_2, yametrics_settings.ACTIVITY_LISTEN)
        manager.action(radio_id_2, yametrics_settings.ACTIVITY_LISTEN)
        manager.action(radio_id_2, yametrics_settings.ACTIVITY_LISTEN)
        
        manager.action(radio_id_3, yametrics_settings.ACTIVITY_LISTEN)
        manager.action(radio_id_3, yametrics_settings.ACTIVITY_LISTEN)
        
        manager.action(radio_id_4, yametrics_settings.ACTIVITY_LISTEN)
        
        manager.compute_progression()
        self.assertEquals(manager.radios.count(), 4)
        
        
        manager.action(radio_id_1, yametrics_settings.ACTIVITY_LISTEN)
        manager.action(radio_id_1, yametrics_settings.ACTIVITY_LISTEN)
        
        
        manager.action(radio_id_2, yametrics_settings.ACTIVITY_LISTEN)
        manager.action(radio_id_2, yametrics_settings.ACTIVITY_LISTEN)
        manager.action(radio_id_2, yametrics_settings.ACTIVITY_LISTEN)
        manager.action(radio_id_2, yametrics_settings.ACTIVITY_LISTEN)
        manager.action(radio_id_2, yametrics_settings.ACTIVITY_LISTEN)
        manager.action(radio_id_2, yametrics_settings.ACTIVITY_LISTEN)
        manager.action(radio_id_2, yametrics_settings.ACTIVITY_LISTEN)
        manager.action(radio_id_2, yametrics_settings.ACTIVITY_LISTEN)
        
        manager.action(radio_id_3, yametrics_settings.ACTIVITY_LISTEN)
        manager.action(radio_id_3, yametrics_settings.ACTIVITY_LISTEN)
        manager.action(radio_id_3, yametrics_settings.ACTIVITY_LISTEN)
        manager.action(radio_id_3, yametrics_settings.ACTIVITY_LISTEN)
        
        manager.action(radio_id_4, yametrics_settings.ACTIVITY_LISTEN)
        manager.action(radio_id_4, yametrics_settings.ACTIVITY_LISTEN)
        manager.action(radio_id_4, yametrics_settings.ACTIVITY_LISTEN)
        manager.action(radio_id_4, yametrics_settings.ACTIVITY_LISTEN)
        
        manager.compute_progression()
        self.assertEquals(manager.radios.count(), 4)
        
        most_popular = manager.most_popular(db_only=False)
        self.assertEquals(most_popular.count(True), 4)
        doc0 = most_popular[0]
        doc1 = most_popular[1]
        doc2 = most_popular[2]
        doc3 = most_popular[3]
        self.assertGreaterEqual(doc0['progression'], doc1['progression'])
        self.assertGreaterEqual(doc1['progression'], doc2['progression'])
        self.assertGreaterEqual(doc2['progression'], doc3['progression'])
        
        most_popular = manager.most_popular(limit=2, db_only=False)
        self.assertEquals(most_popular.count(True), 2)
        
        most_popular = manager.most_popular(skip=1, db_only=False)
        self.assertEquals(most_popular.count(True), 3)
        self.assertEquals(doc1, most_popular[0])
        
        most_popular = manager.most_popular(skip=1, limit=2, db_only=False)
        self.assertEquals(most_popular.count(True), 2)
        self.assertEquals(doc1, most_popular[0])
        self.assertEquals(doc2, most_popular[1])
        
    def test_settings(self):
        manager = RadioPopularityManager()
        factors = {
                   yametrics_settings.ACTIVITY_LISTEN: manager.settings.find({'name':yametrics_settings.ACTIVITY_LISTEN})[0]['value'],
                   yametrics_settings.ACTIVITY_SONG_LIKE: manager.settings.find({'name':yametrics_settings.ACTIVITY_SONG_LIKE})[0]['value'],
                   yametrics_settings.ACTIVITY_WALL_MESSAGE: manager.settings.find({'name':yametrics_settings.ACTIVITY_WALL_MESSAGE})[0]['value'],
                   yametrics_settings.ACTIVITY_SHARE: manager.settings.find({'name':yametrics_settings.ACTIVITY_SHARE})[0]['value'],
                   yametrics_settings.ACTIVITY_ADD_TO_FAVORITES: manager.settings.find({'name':yametrics_settings.ACTIVITY_ADD_TO_FAVORITES})[0]['value']
                   }
        
        # test RadioPopularityManager.action_score_coeff()
        for k in factors:
            self.assertEqual(factors[k], manager.action_score_coeff(k))
            
            
        # test RadioPopularityManager.update_coeff_doc()
        doc = manager.settings.find()[0]
        coeff_id = str(doc['_id'])
        val = 123
        doc['value'] = val
        manager.update_coeff_doc(coeff_id, doc)
        
        doc = manager.settings.find({'_id': ObjectId(coeff_id)})[0]
        self.assertEquals(doc['value'], val)
        
        