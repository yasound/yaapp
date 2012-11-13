from django.conf import settings
from django.contrib.auth.models import User
from pymongo import DESCENDING
from yabase import settings as yabase_settings, signals as yabase_signals
from yabase.models import Radio, SongInstance
from yahistory.task import async_add_listen_radio_event, \
    async_add_post_message_event, async_add_like_song_event, \
    async_add_favorite_radio_event, async_add_not_favorite_radio_event, \
    async_add_share_event, async_add_animator_event, async_add_buy_link_event, async_add_watch_tutorial_event, \
    async_transient_radio_event
from yaref.models import YasoundSong
import datetime
import logging
from bson.objectid import ObjectId

logger = logging.getLogger("yaapp.yahistory")


class UserHistory():
    ETYPE_LISTEN_RADIO = 'listen'
    ETYPE_MESSAGE = 'message'
    ETYPE_LIKE_SONG = 'like_song'
    ETYPE_FAVORITE_RADIO = 'favorite_radio'
    ETYPE_NOT_FAVORITE_RADIO = 'not_favorite_radio'
    ETYPE_SHARE = 'share'
    ETYPE_ANIMATOR = 'animator'
    ETYPE_BUY_LINK = 'buy_link'
    ETYPE_WATCH_TUTORIAL = 'watch_tutorial'

    def __init__(self):
        self.db = settings.MONGO_DB
        self.collection = self.db.history.users
        self.collection.ensure_index("db_id")
        self.collection.ensure_index("date")

    def erase_metrics(self):
        self.collection.drop()

    def _get_radio_name(self, uuid):
        radio = ''
        try:
            radio = Radio.objects.get(uuid=uuid)
        except Radio.DoesNotExist:
            pass
        return unicode(radio)

    def _get_user_name(self, user_id):
        profile = ''
        try:
            user = User.objects.get(id=user_id)
            profile = user.get_profile()
        except Radio.DoesNotExist:
            pass
        return unicode(profile)

    def _get_song_name(self, song_id):
        song = ''
        try:
            song = SongInstance.objects.get(id=song_id)
        except SongInstance.DoesNotExist:
            pass
        return unicode(song)

    def convert_to_new_format(self):
        docs = self.collection.find(snapshot=True)
        for doc in docs:
            radio_data = doc.get('radio')
            if radio_data:
                radio_data['radio_name'] = self._get_radio_name(radio_data.get('uuid'))
                radio_data['radio_uuid'] = radio_data.get('uuid')
                if 'uuid' in radio_data:
                    del radio_data['uuid']

                doc['data'] = radio_data
                del doc['radio']

            message_data = doc.get('message')
            if message_data:
                message_data['radio_name'] = self._get_radio_name(message_data.get('uuid'))
                message_data['radio_uuid'] = message_data.get('uuid')
                if 'uuid' in message_data:
                    del message_data['uuid']

                doc['data'] = message_data
                del doc['message']

            song_data = doc.get('song')
            if song_data:
                song_data['song_name'] = self._get_song_name(song_data.get('db_id'))
                song_data['radio_name'] = self._get_radio_name(song_data.get('uuid'))

                song_data['radio_uuid'] = song_data.get('uuid')
                if 'uuid' in message_data:
                    del message_data['uuid']

                song_data['song_id'] = song_data.get('db_id')
                if 'db_id' in message_data:
                    del song_data['db_id']

                song_data['song_name'] = song_data.get('name')
                if 'name' in message_data:
                    del song_data['name']

                doc['data'] = song_data
                del doc['song']

            self.collection.save(doc)

    def add_event(self, user_id, etype, data):
        doc = {
            'db_id': user_id,
            'user_name': self._get_user_name(user_id),
            'type': etype,
            'date': datetime.datetime.now(),
        }
        doc['data'] = data
        self.collection.insert(doc, safe=True)

    def add_listen_radio_event(self, user_id, radio_uuid):
        data = {
            'radio_uuid': radio_uuid,
            'radio_name': self._get_radio_name(radio_uuid)
        }
        self.add_event(user_id, UserHistory.ETYPE_LISTEN_RADIO, data)

    def add_post_message_event(self, user_id, radio_uuid, message):
        data = {
            'radio_uuid': radio_uuid,
            'radio_name': self._get_radio_name(radio_uuid),
            'message': message,
        }
        self.add_event(user_id, UserHistory.ETYPE_MESSAGE, data)

    def add_like_song_event(self, user_id, radio_uuid, song_id):
        data = {
            'song_id': song_id,
            'radio_uuid': radio_uuid,
            'radio_name': self._get_radio_name(radio_uuid),
            'song_name': self._get_song_name(song_id)
        }
        self.add_event(user_id, UserHistory.ETYPE_LIKE_SONG, data)

    def add_buy_link_event(self, user_id, radio_uuid, song_id):
        data = {
            'song_id': song_id,
            'radio_uuid': radio_uuid,
            'radio_name': self._get_radio_name(radio_uuid),
            'song_name': self._get_song_name(song_id)
        }
        self.add_event(user_id, UserHistory.ETYPE_BUY_LINK, data)

    def add_favorite_radio_event(self, user_id, radio_uuid):
        data = {
            'radio_uuid': radio_uuid,
            'radio_name': self._get_radio_name(radio_uuid),
        }
        self.add_event(user_id, UserHistory.ETYPE_FAVORITE_RADIO, data)

    def add_not_favorite_radio_event(self, user_id, radio_uuid):
        data = {
            'radio_uuid': radio_uuid,
            'radio_name': self._get_radio_name(radio_uuid),
        }
        self.add_event(user_id, UserHistory.ETYPE_NOT_FAVORITE_RADIO, data)

    def add_share_event(self, user_id, radio_uuid, share_type):
        data = {
            'radio_uuid': radio_uuid,
            'radio_name': self._get_radio_name(radio_uuid),
            'share_type': share_type
        }
        self.add_event(user_id, UserHistory.ETYPE_SHARE, data)

    def add_animator_event(self, user_id, radio_uuid, atype, details=None):
        data = {
            'radio_uuid': radio_uuid,
            'radio_name': self._get_radio_name(radio_uuid),
            'atype': atype
        }
        if details is not None:
            if atype in [yabase_settings.ANIMATOR_TYPE_REJECT_SONG, yabase_settings.ANIMATOR_TYPE_DELETE_SONG]:
                song_instance = details.get('song_instance', '')
                data['song_name'] = unicode(song_instance)
            elif atype == yabase_settings.ANIMATOR_TYPE_ADD_SONG:
                yasound_song_id = details.get('yasound_song_id', None)
                if yasound_song_id:
                    data['song_name'] = unicode(YasoundSong.objects.get(id=yasound_song_id))

        self.add_event(user_id, UserHistory.ETYPE_ANIMATOR, data)

    def add_watch_tutorial_event(self, user_id):
        self.add_event(user_id, UserHistory.ETYPE_WATCH_TUTORIAL, data=None)

    def all(self, user_id=None, start=0, limit=25):
        if user_id:
            docs = self.collection.find({'db_id': user_id}).skip(start).limit(limit).sort([('date', DESCENDING)])
        else:
            docs = self.collection.find().skip(start).limit(limit).sort([('date', DESCENDING)])
        return docs

    def last_message(self, user_id):
        return self.collection.find_one({'db_id': user_id, 'type': UserHistory.ETYPE_MESSAGE}, sort=[('date', DESCENDING)])

    def history_for_user(self, user_id, start_date=None, end_date=None, infinite=False, etype=None):
        query = {'db_id': user_id}
        if not infinite:
            if end_date is None:
                end_date = datetime.date.now()
            if start_date is None:
                start_date = start_date + datetime.timedelta(days=-1)

            query['date'] = {"$gte": start_date, "$lte": end_date}
        if etype:
            query['type'] = etype

        return self.collection.find(query).sort([('start_date', DESCENDING)])


class ProgrammingHistory():
    PTYPE_UPLOAD_PLAYLIST = 'upload_playlist'
    PTYPE_UPLOAD_FILE = 'upload_file'
    PTYPE_ADD_FROM_YASOUND = 'add_from_yasound'
    PTYPE_ADD_FROM_DEEZER = 'add_from_deezer'
    PTYPE_IMPORT_FROM_ITUNES = 'import_from_itunes'
    PTYPE_REMOVE_FROM_PLAYLIST = 'remove_from_playlist'

    STATUS_SUCCESS = 'success'
    STATUS_FINISHED = 'finished'
    STATUS_FAILED = 'failed'
    STATUS_PENDING = 'pending'

    def __init__(self):
        self.db = settings.MONGO_DB
        self.collection = self.db.history.programming
        self.details = self.db.history.programming.details
        self.collection.ensure_index("user_id")
        self.collection.ensure_index("radio_id")
        self.collection.ensure_index("updated")
        self.collection.ensure_index("status")

        self.details.ensure_index('event_id')

    def erase_metrics(self):
        self.collection.drop()
        self.details.drop()

    def generate_event(self, event_type, status=STATUS_PENDING, user=None, radio=None, data=None):
        now = datetime.datetime.now()
        doc = {
            'created': now,
            'updated': now,
            'radio_id': radio.id if radio is not None else None,
            'user_id': user.id if user is not None else None,
            'status': status,
            'type': event_type,
        }
        doc_id = self.collection.insert(doc, safe=True)
        return self.collection.find_one({'_id': doc_id})

    def add_details(self, event, details):
        details['event_id'] = event.get('_id')
        return self.details.insert(details, safe=True)

    def add_details_success(self, event, details):
        details['status'] = ProgrammingHistory.STATUS_SUCCESS
        return self.add_details(event, details)

    def add_details_failed(self, event, details):
        details['status'] = ProgrammingHistory.STATUS_FAILED
        return self.add_details(event, details)

    def update_event(self, event):
        now = datetime.datetime.now()
        event['updated'] = now
        doc_id = self.collection.save(event, safe=True)
        return self.collection.find_one({'_id': doc_id})

    def find_event(self, event_id):
        if isinstance(event_id, str) or isinstance(event_id, unicode):
            event_id = ObjectId(event_id)
        return self.collection.find_one({'_id': event_id})

    def finished(self, event):
        event['status'] = ProgrammingHistory.STATUS_FINISHED
        return self.update_event(event)

    def success(self, event):
        event['status'] = ProgrammingHistory.STATUS_SUCCESS
        return self.update_event(event)

    def failed(self, event):
        event['status'] = ProgrammingHistory.STATUS_FAILED
        return self.update_event(event)

    def events_for_user(self, user, status=None):
        if status:
            return self.collection.find({'user_id': user.id, 'status': status}).sort([('updated', DESCENDING)])
        else:
            return self.collection.find({'user_id': user.id}).sort([('updated', DESCENDING)])

    def events_for_radio(self, radio, status=None, skip=None, limit=None):
        if status:
            qs = self.collection.find({'radio_id': radio.id, 'status': status})
        else:
            qs = self.collection.find({'radio_id': radio.id})

        if skip is not None:
            qs = qs.skip(skip)

        if limit:
            qs = qs.limit(limit)

        return qs.sort([('updated', DESCENDING)])

    def details_for_event(self, event, status=None):
        if status:
            return self.details.find({'event_id': event.get('_id'), 'status': status})
        else:
            return self.details.find({'event_id': event.get('_id')})

    def remove_event(self, event):
        self.details.remove({'event_id': event.get('_id')}, safe=True)
        self.collection.remove({'_id': event.get('_id')}, safe=True)


class TransientRadioHistory():
    TYPE_PLAYLIST_ADDED = 'playlist_added'
    TYPE_PLAYLIST_UPDATED = 'playlist_updated'
    TYPE_PLAYLIST_DELETED = 'playlist_deleted'

    TYPE_RADIO_ADDED = 'radio_added'
    TYPE_RADIO_DELETED = 'radio_deleted'

    def __init__(self):
        self.db = settings.MONGO_DB
        self.collection = self.db.history.transient.playlist
        self.collection.ensure_index("radio_uuid")
        self.collection.ensure_index("playlist_id")

    def erase_informations(self):
        self.collection.drop()

    def add_event(self, event_type, radio_uuid, playlist_id):
        now = datetime.datetime.now()
        doc = {
            'created': now,
            'updated': now,
            'radio_uuid': radio_uuid,
            'playlist_id': playlist_id,
            'type': event_type,
        }
        self.collection.insert(doc, safe=True)

# event handlers


def user_started_listening_handler(sender, radio, user, **kwargs):
    if not user.is_anonymous():
        async_add_listen_radio_event.delay(user.id, radio.uuid)


def user_watched_tutorial_handler(sender, user, **kwargs):
    if not user.is_anonymous():
        async_add_watch_tutorial_event.delay(user.id)


def new_wall_event_handler(sender, wall_event, **kwargs):
    user = wall_event.user
    if user is None:
        return
    if user.is_anonymous():
        return

    we_type = wall_event.type
    if we_type == yabase_settings.EVENT_MESSAGE:
        async_add_post_message_event.delay(user.id, wall_event.radio.uuid, wall_event.text)

    elif we_type == yabase_settings.EVENT_LIKE:
        async_add_like_song_event.delay(user.id, wall_event.radio.uuid, wall_event.song.id)


def favorite_radio_handler(sender, radio, user, **kwargs):
    async_add_favorite_radio_event.delay(user.id, radio.uuid)


def not_favorite_radio_handler(sender, radio, user, **kwargs):
    async_add_not_favorite_radio_event.delay(user.id, radio.uuid)


def new_share(sender, radio, user, share_type, **kwargs):
    async_add_share_event.delay(user.id, radio.uuid, share_type=share_type)


def new_animator_activity(sender, user, radio, atype, details=None, **kwargs):
    if radio is not None:
        async_add_animator_event.delay(user.id, radio.uuid, atype, details=details)


def buy_link_handler(sender, radio, user, song_instance, **kwargs):
    if user is None:
        return
    if user.is_anonymous():
        return
    async_add_buy_link_event.delay(user.id, radio.uuid, song_instance.id)


def radio_deleted_handler(sender, radio, **kwargs):
    async_transient_radio_event.delay(event_type=TransientRadioHistory.TYPE_RADIO_DELETED, radio_uuid=radio.uuid)


def install_handlers():
    yabase_signals.user_watched_tutorial.connect(user_watched_tutorial_handler)
    yabase_signals.user_started_listening.connect(user_started_listening_handler)
    yabase_signals.new_wall_event.connect(new_wall_event_handler)
    yabase_signals.favorite_radio.connect(favorite_radio_handler)
    yabase_signals.not_favorite_radio.connect(not_favorite_radio_handler)
    yabase_signals.radio_shared.connect(new_share)
    yabase_signals.new_animator_activity.connect(new_animator_activity)
    yabase_signals.buy_link.connect(buy_link_handler)

    yabase_signals.radio_deleted.connect(radio_deleted_handler)
install_handlers()
