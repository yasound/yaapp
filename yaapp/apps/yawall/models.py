import time
import datetime
from django.conf import settings
from yabase.models import SongInstance
from django.core.cache import cache
import json
from pymongo import DESCENDING
import logging
logger = logging.getLogger("yaapp.yawall")
import dateutil.parser

LOCK_EXPIRE = 60 * 1  # Lock expires in 1 minute(s)


class WallManager():
    EVENT_LIKE = 'like'
    EVENT_MESSAGE = 'message'
    WAIT_FOR_LOCK = 10  # wait 10 seconds

    def __init__(self):
        self.db = settings.MONGO_DB
        self.collection = self.db.wall
        self.collection.ensure_index('radio_uuid')
        self.collection.ensure_index('event_id')
        self.collection.ensure_index('updated')

    def _generate_event_id(self, radio, current_song):
        now = datetime.datetime.now()
        song_date = current_song.get('last_play_time')
        if song_date is not None:
            song_date = dateutil.parser.parse(song_date)
        else:
            song_date = now

        time_val = time.mktime(song_date.timetuple())
        return '%s-%s' % (radio.uuid, time_val)

    def _create_blank_current_song(self):
        now = datetime.datetime.now()
        current_song = {
            'name': '',
            'artist': '',
            'last_play_time': now,
            'large_cover_url': settings.DEFAULT_TRACK_IMAGE,
            'cover_url': settings.DEFAULT_TRACK_IMAGE,
        }
        return current_song

    def _generate_title(self, current_song):
        artist = current_song.get('artist', '')
        name = current_song.get('name', '')

        if artist != '' and name != '':
            return u'%s - %s' % (name, artist)

        if name != '':
            return name

        return ''

    def add_event(self, event_type, radio, user, message=None):
        lock_id = "wall-add-event-lock"
        acquire_lock = lambda: cache.add(lock_id, "true", LOCK_EXPIRE)
        release_lock = lambda: cache.delete(lock_id)

        retry = 0
        max_retry = 3
        while not acquire_lock():
            time.sleep(WallManager.WAIT_FOR_LOCK)
            retry += 1
            if retry > max_retry:
                return

        now = datetime.datetime.now()
        current_song_json = SongInstance.objects.get_current_song_json(radio.id)
        if current_song_json is not None:
            current_song = json.loads(current_song_json)
        else:
            current_song = self._create_blank_current_song()

        event_id = self._generate_event_id(radio, current_song)
        title = self._generate_title(current_song)

        doc = self.collection.find_one({'event_id': event_id}, {'_id': False})
        if doc is None:
            doc = {
                'event_type': event_type,
                'radio_uuid': radio.uuid,
                'title': title,
                'current_song': current_song,
                'created': now,
                'event_id': event_id,
                'messages': [],
                'likes': [],
                'likers_digest': [],
                'like_count': 0,
                'message_count': 0
            }
        doc['updated'] = now
        doc['title'] = title

        if event_type == WallManager.EVENT_MESSAGE:
            message_data = {
                'text': message,
                'name': unicode(user.get_profile()),
                'username': user.username,
            }
            doc.get('messages').insert(0, message_data)
            doc['message_count'] = doc.get('message_count', 0) + 1

        elif event_type == WallManager.EVENT_LIKE:
            like_data = {
                'name': unicode(user.get_profile()),
                'username': user.username,
            }
            already_liked = False
            for like in doc.get('likes', []):
                if like.get('username') == user.username:
                    already_liked = True
                    break
            if not already_liked:
                doc.get('likes').append(like_data)
                doc['like_count'] = doc.get('like_count', 0) + 1

            likers = doc.get('likes')
            likers_digest = []
            for like in likers[:3]:
                likers_digest.append(like)
            doc['liker_digest'] = likers_digest

        self.collection.update({"event_id": doc.get('event_id')},
                               {"$set": doc}, upsert=True, safe=True)

        release_lock()

    def events_for_radio(self, radio_uuid, skip=0, limit=20):
        return self.collection.find({
            'radio_uuid': radio_uuid,
        }).sort([('updated', DESCENDING)]).skip(skip).limit(limit)

    def events_count_for_radio(self, radio_uuid):
        return self.collection.find({
            'radio_uuid': radio_uuid,
        }).count()
