from django.contrib.auth.models import User
from django.test import TestCase
from models import UserHistory, ProgrammingHistory
from yabase.models import Radio
import datetime
from yabase import settings as yabase_settings


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
        r = Radio.objects.create(name='pizza', ready=False, creator=self.user)
        uh.add_listen_radio_event(user_id=self.user.id, radio_uuid=r.uuid)

        now = datetime.datetime.now()
        yesterday = now + datetime.timedelta(days=-1)

        docs = uh.history_for_user(self.user.id, start_date=yesterday, end_date=now)
        self.assertEquals(docs.count(), 1)

        doc = docs[0]

        self.assertEquals(doc['db_id'], self.user.id)

        docs = uh.history_for_user(self.user.id, infinite=True, etype=UserHistory.ETYPE_LISTEN_RADIO)
        self.assertEquals(docs.count(), 1)

    def test_add_listen_radio_event2(self):
        uh = UserHistory()
        r = Radio.objects.create(name='pizza', ready=False, creator=self.user)
        uh.add_listen_radio_event(user_id=self.user.id, radio_uuid=r.uuid)

        now = datetime.datetime.now()
        yesterday = now + datetime.timedelta(days=-1)

        docs = uh.history_for_user(self.user.id, start_date=yesterday, end_date=now)
        self.assertEquals(docs.count(), 1)

        doc = docs[0]

        self.assertEquals(doc['db_id'], self.user.id)

        docs = uh.history_for_user(self.user.id, infinite=True, etype=UserHistory.ETYPE_LISTEN_RADIO)
        self.assertEquals(docs.count(), 1)

    def test_add_watch_tutorial_event(self):
        uh = UserHistory()
        uh.add_watch_tutorial_event(user_id=self.user.id)

        now = datetime.datetime.now()
        yesterday = now + datetime.timedelta(days=-1)

        docs = uh.history_for_user(self.user.id, start_date=yesterday, end_date=now)
        self.assertEquals(docs.count(), 1)

        doc = docs[0]

        self.assertEquals(doc['db_id'], self.user.id)

        docs = uh.history_for_user(self.user.id, infinite=True, etype=UserHistory.ETYPE_WATCH_TUTORIAL)
        self.assertEquals(docs.count(), 1)

    def test_add_post_message_event(self):
        uh = UserHistory()
        r = Radio.objects.create(name='pizza', ready=False, creator=self.user)
        uh.add_post_message_event(user_id=self.user.id, radio_uuid=r.uuid, message=u'hello, world')

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

        doc = uh.last_message(self.user.id)
        self.assertEquals(doc.get('data').get('message'), u'hello, world')

        uh.add_post_message_event(user_id=self.user.id, radio_uuid=r.uuid, message=u'second message')

        doc = uh.last_message(self.user.id)
        self.assertEquals(doc.get('data').get('message'), u'second message')

    def test_add_like_song_event(self):
        uh = UserHistory()
        r = Radio.objects.create(name='pizza', ready=False, creator=self.user)
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
        r = Radio.objects.create(name='pizza', ready=False, creator=self.user)
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
        r = Radio.objects.create(name='pizza', ready=False, creator=self.user)
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
        r = Radio.objects.create(name='pizza', ready=False, creator=self.user)
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

        r = Radio.objects.create(name='pizza', ready=False, creator=self.user)
        uh.add_animator_event(user_id=self.user.id, radio_uuid=r.uuid, atype=yabase_settings.ANIMATOR_TYPE_IMPORT_ITUNES)

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


class TestProgrammingHistory(TestCase):
    def setUp(self):
        pm = ProgrammingHistory()
        pm.erase_metrics()

        user = User(email="test@yasound.com", username="test", is_superuser=False, is_staff=False)
        user.set_password('test')
        user.save()
        self.client.login(username="test", password="test")
        self.user = user

    def test_insert_event(self):
        pm = ProgrammingHistory()
        doc = pm.generate_event(ProgrammingHistory.PTYPE_UPLOAD_PLAYLIST)
        self.assertTrue(doc.get('_id') is not None)
        self.assertEquals(doc.get('status'), ProgrammingHistory.STATUS_PENDING)

    def test_update_event(self):
        pm = ProgrammingHistory()
        doc = pm.generate_event(ProgrammingHistory.PTYPE_UPLOAD_PLAYLIST)
        prevId = doc.get('_id')

        doc['user_id'] = self.user.id
        doc['status'] = ProgrammingHistory.STATUS_FINISHED
        doc['data'] = {
            'key': 'value'
        }
        doc = pm.update_event(doc)
        self.assertEquals(doc.get('_id'), prevId)
        self.assertEquals(doc.get('status'), ProgrammingHistory.STATUS_FINISHED)

    def test_add_details(self):
        pm = ProgrammingHistory()
        doc = pm.generate_event(ProgrammingHistory.PTYPE_UPLOAD_PLAYLIST)
        prevId = doc.get('_id')

        details = {
            'artist': 'artist',
            'status': ProgrammingHistory.STATUS_SUCCESS
        }
        pm.add_details(doc, details)

        details = pm.details_for_event(doc)
        self.assertEquals(details.count(), 1)

        details2 = {
            'artist': 'artist2'
        }
        pm.add_details_success(doc, details2)

        details3 = {
            'artist': 'artist3'
        }
        pm.add_details_failed(doc, details3)

        success = pm.details_for_event(doc, status=ProgrammingHistory.STATUS_SUCCESS)
        self.assertEquals(success.count(), 2)

        failed = pm.details_for_event(doc, status=ProgrammingHistory.STATUS_FAILED)
        self.assertEquals(failed.count(), 1)
