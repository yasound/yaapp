from django.contrib.auth.models import User
from django.test import TestCase
from models import UserHistory
from yabase.models import Radio
import datetime
class TestGlobalMetricsManager(TestCase):
    def setUp(self):
        uh = UserHistory()
        uh.erase_metrics()

        user = User(email="test@yasound.com", username="test", is_superuser=False, is_staff=False)
        user.set_password('test')
        user.save()
        self.client.login(username="test", password="test")
        self.user = user        
    
    def test_add_listen_radio_event(self):
        uh = UserHistory()
        r = Radio.objects.create(name='pizza', ready=True, creator=self.user)
        uh.add_listen_radio_event(user_id=self.user.id, radio_uuid=r.uuid)

        now = datetime.datetime.now()
        yesterday = now + datetime.timedelta(days=-1)
        
        docs = uh.history_for_user(self.user.id, start_date=yesterday, end_date=now)
        self.assertEquals(docs.count(), 1)
        
        doc = docs[0]

        self.assertEquals(doc['db_id'], self.user.id)

        docs = uh.history_for_user(self.user.id, infinite=True, etype=UserHistory.ETYPE_LISTEN_RADIO)
        self.assertEquals(docs.count(), 1)

    def test_add_post_message_event(self):
        uh = UserHistory()
        r = Radio.objects.create(name='pizza', ready=True, creator=self.user)
        uh.add_post_message_event(user_id=self.user.id, radio_uuid=r.uuid, message=u'hello, word')

        now = datetime.datetime.now()
        yesterday = now + datetime.timedelta(days=-1)
        
        docs = uh.history_for_user(self.user.id, start_date=yesterday, end_date=now)
        self.assertEquals(docs.count(), 1)
        
        doc = docs[0]

        self.assertEquals(doc['db_id'], self.user.id)

        docs = uh.history_for_user(self.user.id, infinite=True, etype=UserHistory.ETYPE_MESSAGE)
        self.assertEquals(docs.count(), 1)

        docs = uh.history_for_user(self.user.id, infinite=True, etype=UserHistory.ETYPE_LIKE_SONG)
        self.assertEquals(docs.count(), 0)

    def test_add_like_song_event(self):
        uh = UserHistory()
        r = Radio.objects.create(name='pizza', ready=True, creator=self.user)
        uh.add_like_song_event(user_id=self.user.id, radio_uuid=r.uuid, song_id=42)

        now = datetime.datetime.now()
        yesterday = now + datetime.timedelta(days=-1)
        
        docs = uh.history_for_user(self.user.id, start_date=yesterday, end_date=now)
        self.assertEquals(docs.count(), 1)
        
        doc = docs[0]

        self.assertEquals(doc['db_id'], self.user.id)

        docs = uh.history_for_user(self.user.id, infinite=True, etype=UserHistory.ETYPE_LIKE_SONG)
        self.assertEquals(docs.count(), 1)

        docs = uh.history_for_user(self.user.id, infinite=True, etype=UserHistory.ETYPE_LISTEN_RADIO)
        self.assertEquals(docs.count(), 0)
                
    def test_add_favorite_radio_event(self):
        uh = UserHistory()
        r = Radio.objects.create(name='pizza', ready=True, creator=self.user)
        uh.add_favorite_radio_event(user_id=self.user.id, radio_uuid=r.uuid)

        now = datetime.datetime.now()
        yesterday = now + datetime.timedelta(days=-1)
        
        docs = uh.history_for_user(self.user.id, start_date=yesterday, end_date=now)
        self.assertEquals(docs.count(), 1)
        
        doc = docs[0]

        self.assertEquals(doc['db_id'], self.user.id)

        docs = uh.history_for_user(self.user.id, infinite=True, etype=UserHistory.ETYPE_FAVORITE_RADIO)
        self.assertEquals(docs.count(), 1)

        docs = uh.history_for_user(self.user.id, infinite=True, etype=UserHistory.ETYPE_LISTEN_RADIO)
        self.assertEquals(docs.count(), 0)       
        
    def test_add_not_favorite_radio_event(self):
        uh = UserHistory()
        r = Radio.objects.create(name='pizza', ready=True, creator=self.user)
        uh.add_not_favorite_radio_event(user_id=self.user.id, radio_uuid=r.uuid)

        now = datetime.datetime.now()
        yesterday = now + datetime.timedelta(days=-1)
        
        docs = uh.history_for_user(self.user.id, start_date=yesterday, end_date=now)
        self.assertEquals(docs.count(), 1)
        
        doc = docs[0]

        self.assertEquals(doc['db_id'], self.user.id)

        docs = uh.history_for_user(self.user.id, infinite=True, etype=UserHistory.ETYPE_NOT_FAVORITE_RADIO)
        self.assertEquals(docs.count(), 1)

        docs = uh.history_for_user(self.user.id, infinite=True, etype=UserHistory.ETYPE_LISTEN_RADIO)
        self.assertEquals(docs.count(), 0)       

    def test_add_share_event(self):
        uh = UserHistory()
        r = Radio.objects.create(name='pizza', ready=True, creator=self.user)
        uh.add_share_event(user_id=self.user.id, radio_uuid=r.uuid, share_type='email')

        now = datetime.datetime.now()
        yesterday = now + datetime.timedelta(days=-1)
        
        docs = uh.history_for_user(self.user.id, start_date=yesterday, end_date=now)
        self.assertEquals(docs.count(), 1)
        
        doc = docs[0]

        self.assertEquals(doc['db_id'], self.user.id)

        docs = uh.history_for_user(self.user.id, infinite=True, etype=UserHistory.ETYPE_SHARE)
        self.assertEquals(docs.count(), 1)

        docs = uh.history_for_user(self.user.id, infinite=True, etype=UserHistory.ETYPE_LISTEN_RADIO)
        self.assertEquals(docs.count(), 0)       

    def test_add_animator_event(self):
        uh = UserHistory()
        r = Radio.objects.create(name='pizza', ready=True, creator=self.user)
        uh.add_animator_event(user_id=self.user.id, radio_uuid=r.uuid)

        now = datetime.datetime.now()
        yesterday = now + datetime.timedelta(days=-1)
        
        docs = uh.history_for_user(self.user.id, start_date=yesterday, end_date=now)
        self.assertEquals(docs.count(), 1)
        
        doc = docs[0]

        self.assertEquals(doc['db_id'], self.user.id)

        docs = uh.history_for_user(self.user.id, infinite=True, etype=UserHistory.ETYPE_ANIMATOR)
        self.assertEquals(docs.count(), 1)

        docs = uh.history_for_user(self.user.id, infinite=True, etype=UserHistory.ETYPE_LISTEN_RADIO)
        self.assertEquals(docs.count(), 0)       
