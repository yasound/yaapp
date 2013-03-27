from django.conf import settings
from django.db.models.signals import pre_delete
from yabase import signals as yabase_signals
import datetime
import logging
from task import async_transient_radio_event
from yabase import settings as yabase_settings
from yabase.models import Playlist
from redis import Redis
import json

logger = logging.getLogger("yaapp.yascheduler")


class TransientRadioHistoryManager():
    TYPE_PLAYLIST_ADDED = 'playlist_added'
    TYPE_PLAYLIST_UPDATED = 'playlist_updated'
    TYPE_PLAYLIST_DELETED = 'playlist_deleted'

    TYPE_JINGLE_ADDED = 'jingle_added'
    TYPE_JINGLE_UPDATED = 'jingle_updated'
    TYPE_JINGLE_DELETED = 'jingle_deleted'

    TYPE_RADIO_ADDED = 'radio_added'
    TYPE_RADIO_DELETED = 'radio_deleted'

    def __init__(self):
        self.db = settings.MONGO_DB
        self.collection = self.db.scheduler.transient.radios
        self.collection.ensure_index("radio_uuid")
        self.collection.ensure_index("playlist_id")
        self.collection.ensure_index("updated")

    def erase_informations(self):
        self.collection.drop()

    def add_event(self, event_type, radio_uuid, playlist_id, jingle_id=None):
        now = datetime.datetime.now()
        doc = {
            'created': now,
            'updated': now,
            'radio_uuid': radio_uuid,
            'playlist_id': playlist_id,
            'jingle_id': jingle_id,
            'type': event_type,
        }
        self.collection.update({'radio_uuid': radio_uuid}, doc, upsert=True, safe=True)
        self.notify_yascheduler()

    def events_for_radio(self, radio_uuid):
        return self.collection.find({'radio_uuid': radio_uuid})

    def notify_yascheduler(self):
        red = Redis(host=settings.YASCHEDULER_REDIS_HOST, db=0)
        channel = 'yaapp'
        data = {
            'event_type': 'radio_updated',
        }
        json_data = json.JSONEncoder(ensure_ascii=False).encode(data)
        red.publish(channel, json_data)


def radio_deleted_handler(sender, radio, **kwargs):
    async_transient_radio_event.delay(event_type=TransientRadioHistoryManager.TYPE_RADIO_DELETED, radio_uuid=radio.uuid)


def animator_activity_handler(sender, user, radio, atype, details=None, playlist=None, **kwargs):
    playlist_update_types = (
        yabase_settings.ANIMATOR_TYPE_UPLOAD_PLAYLIST,
        yabase_settings.ANIMATOR_TYPE_UPLOAD_SONG,
        yabase_settings.ANIMATOR_TYPE_ADD_SONG,
        yabase_settings.ANIMATOR_TYPE_REJECT_SONG,
        yabase_settings.ANIMATOR_TYPE_DELETE_SONG,
        yabase_settings.ANIMATOR_TYPE_IMPORT_ITUNES,
    )

    if atype == yabase_settings.ANIMATOR_TYPE_CREATE_RADIO:
        async_transient_radio_event.delay(event_type=TransientRadioHistoryManager.TYPE_RADIO_ADDED, radio_uuid=radio.uuid)
    elif atype in playlist_update_types:
        if playlist is None:
            playlist, created = radio.get_or_create_default_playlist()
        async_transient_radio_event.delay(event_type=TransientRadioHistoryManager.TYPE_PLAYLIST_UPDATED, radio_uuid=radio.uuid, playlist_id=playlist.id)


def playlist_deleted_handler(sender, instance, created=None, **kwargs):
    playlist = instance
    async_transient_radio_event.delay(event_type=TransientRadioHistoryManager.TYPE_PLAYLIST_DELETED, radio_uuid=playlist.radio.uuid, playlist_id=playlist.id)


def install_handlers():
    yabase_signals.radio_deleted.connect(radio_deleted_handler)
    yabase_signals.new_animator_activity.connect(animator_activity_handler)
    pre_delete.connect(playlist_deleted_handler, sender=Playlist)
install_handlers()
