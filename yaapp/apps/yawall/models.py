# -*- coding: utf-8 -*-
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
import hashlib
import signals as yawall_signals
import uuid
from yasearch.utils import get_simplified_name

LOCK_EXPIRE = 60 * 1  # Lock expires in 1 minute(s)


class WallManager():
    """Store wall events in mongodb.

    A wall event can be::

    * like
    * message

    like::

        { "_id" : ObjectId( "50d18e3712e5950fbd60a4a1" ),
          "created" : Date( 1355914311407 ),
          "current_song" : { "artist_server" : "Feist",
            "album" : "Let It Die",
            "large_cover" : "/media/images/default_album.jpg",
            "artist_simplified" : "feist",
            "name" : "Let it die",
            "name_server" : "Let it die",
            "artist" : "Feist",
            "album_client" : "Thriller",
            "enabled" : true,
            "cover" : "/media/images/default_album.jpg",
            "id" : 1,
            "last_play_time" : "2012-11-26T23:11:26.911373",
            "frequency" : 0.5,
            "name_simplified" : "let it die",
            "album_server" : "Let It Die",
            "need_sync" : false,
            "name_client" : "Billie Jean",
            "artist_client" : "Mickael Jackson",
            "order" : null,
            "album_simplified" : "let it die",
            "likes" : 2 },
          "event_id" : "4b58a6e208c14a5c8718262877d4da57-like-1353967886.0",
          "event_type" : "like",
          "like_count" : 1,
          "likers" : [
            { "username" : "jerome",
              "updated" : Date( 1355916716021 ),
              "name" : "Jérôme Blondon",
              "created" : Date( 1355914311407 ) } ],
          "likers_digest" : [
            { "username" : "jerome",
              "updated" : Date( 1355916716021 ),
              "name" : "Jérôme Blondon",
              "created" : Date( 1355914311407 ) } ],
          "message" : {},
          "message_count" : 0,
          "radio_id" : 1,
          "radio_uuid" : "4b58a6e208c14a5c8718262877d4da57",
          "song_uuid" : "2dbb1ec99fea3861dabf595f3aa0ec5c",
          "title" : "Let it die - Feist",
          "updated" : Date( 1355916716021 ) }

    message::

        { "_id" : ObjectId( "50d1c26712e5950fbd60a4b2" ),
          "created" : Date( 1355927671325 ),
          "current_song" : { "large_cover" : "http://www.k-fm.com/wp-content/plugins/4ways/_radio/pochettes/Yoon Mi Rae Tasha Get It In.jpg~210",
            "cover" : "http://www.k-fm.com/wp-content/plugins/4ways/_radio/pochettes/Yoon Mi Rae Tasha Get It In.jpg~32",
            "name" : "Get It In (Feat. Tiger JK)",
            "artist" : "YOON MI RAE (TASHA)" },
          "event_id" : "eb029b2e37254170a03652addcce6afd-msg-1355924071.0",
          "event_type" : "message",
          "like_count" : 0,
          "likers" : [],
          "likers_digest" : [],
          "message" : { "username" : "jerome",
            "text" : "There is a hard disk failure, replace the drive immediately.",
            "name" : "Jérôme Blondon",
            "created" : Date( 1355927671325 ) },
          "message_count" : 0,
          "radio_id" : 8,
          "radio_uuid" : "eb029b2e37254170a03652addcce6afd",
          "song_uuid" : "77478e5c800a31f64b9143f5d4995059",
          "title" : "Get It In (Feat. Tiger JK) - YOON MI RAE (TASHA)",
          "updated" : Date( 1355927671325 ) }
    """

    EVENT_LIKE = 'like'
    EVENT_MESSAGE = 'message'
    WAIT_FOR_LOCK = 10  # wait 10 seconds

    def __init__(self):
        self.db = settings.MONGO_DB
        self.collection = self.db.wall
        self.collection.ensure_index('radio_uuid')
        self.collection.ensure_index('event_id')
        self.collection.ensure_index('song_uuid')
        self.collection.ensure_index('updated')

    def _generate_event_id(self, radio, event_type, current_song):
        if event_type == WallManager.EVENT_MESSAGE:
            now = datetime.datetime.now()
            time_val = time.mktime(now.timetuple())
            return '%s-msg-%s' % (radio.uuid, time_val)
        elif event_type == WallManager.EVENT_LIKE:
            song_date = current_song.get('last_play_time')
            try:
                song_date = dateutil.parser.parse(song_date)
            except:
                song_date = datetime.datetime.now()

            time_val = time.mktime(song_date.timetuple())
            return '%s-like-%s' % (radio.uuid, time_val)

    def _generate_song_uuid(self, current_song):
        """ generate a unique uuid from song """
        hash_name = hashlib.md5()
        hash_name.update(get_simplified_name(current_song.get('name', '')))
        hash_name.update(get_simplified_name(current_song.get('album', '')))
        hash_name.update(get_simplified_name(current_song.get('artist', '')))
        hash_name = hash_name.hexdigest()
        return hash_name

    def _create_blank_current_song(self):
        now = datetime.datetime.now()
        current_song = {
            'name': '',
            'artist': '',
            'album': '',
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

    def _likers_for_song(self, radio_uuid, song_uuid):
        likers = []
        filters = {
            'radio_uuid': radio_uuid,
            'song_uuid': song_uuid
        }
        res = self.collection.find(filters, {'likers': True})
        for doc in res:
            likers.extend(doc.get('likers', []))
        return likers

    def add_event(self, event_type, radio, user, message=None):
        """Add a new event to the wall

        :param event_type: like or message
        :param radio: radio
        :param user: user
        :param message: message when event_type is 'message'
        """

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

        event_id = self._generate_event_id(radio, event_type, current_song)
        title = self._generate_title(current_song)

        doc = self.collection.find_one({'event_id': event_id}, {'_id': False})
        if doc is None:
            doc = {
                'radio_id': radio.id,
                'event_type': event_type,
                'radio_uuid': radio.uuid,
                'title': title,
                'current_song': current_song,
                'created': now,
                'event_id': event_id,
                'message': {},
                'likers': [],
                'likers_digest': [],
                'like_count': 0,
                'message_count': 0
            }
        song_uuid = self._generate_song_uuid(current_song)
        doc['updated'] = now
        doc['title'] = title
        doc['radio_id'] = radio.id
        doc['radio_uuid'] = radio.uuid
        doc['song_uuid'] = song_uuid
        doc['event_type'] = event_type

        if event_type == WallManager.EVENT_MESSAGE:
            message_data = {
                'text': message,
                'name': unicode(user.get_profile()),
                'created': now,
                'username': user.username,
            }
            doc['message'] = message_data

        elif event_type == WallManager.EVENT_LIKE:
            previous_likers = self._likers_for_song(radio.uuid, song_uuid)
            likers = []
            like_data = {
                'name': unicode(user.get_profile()),
                'created': now,
                'updated': now,
                'username': user.username,
            }
            for liker in previous_likers:
                if liker.get('username') == user.username:
                    # save original creation date
                    like_data['created'] = liker.get('created')
                    continue
                likers.append(liker)

            likers.insert(0, like_data)

            doc['likers'] = likers
            doc['like_count'] = len(likers)

            likers_digest = []
            for like in likers[:3]:
                likers_digest.append(like)
            doc['likers_digest'] = likers_digest

        self.collection.update({"event_id": doc.get('event_id')},
                               {"$set": doc}, upsert=True, safe=True)

        release_lock()
        yawall_signals.wall_event_updated.send(sender=self, event=doc)

    def events_for_radio(self, radio_uuid, skip=0, limit=20):
        """return the events for the given radio

        :param skip: skip
        :param limit: limit (default=20)
        :return: mongodb cursor
        """

        return self.collection.find({
            'radio_uuid': radio_uuid,
        }).sort([('updated', DESCENDING)]).skip(skip).limit(limit)

    def events_count_for_radio(self, radio_uuid):
        """return the total number of events for a given radio

        :return: events count
        """
        return self.collection.find({
            'radio_uuid': radio_uuid,
        }).count()

    def remove_event(self, event_id):
        """remove definitively the event

        :param event_id: event_id (not _id)
        """
        event = self.collection.find_one({'event_id': event_id})
        if event:
            yawall_signals.wall_event_deleted.send(sender=self, event=event)
            self.collection.remove({'event_id': event_id}, safe=True)

    def event(self, event_id):
        """return event doc

        :param event_id: event_id (not _id)
        :return: full event doc
        """
        return self.collection.find_one({'event_id': event_id})

    def mark_as_abuse(self, event_id):
        """mark event as abuse

        :param event_id: event_id (not _id)
        """
        self.collection.update({
            'event_id': event_id
        }, {
            '$set': {'abuse': True}
        }, safe=True)


if settings.ENABLE_PUSH:
    from push import install_handlers
    install_handlers()
