from account.models import UserProfile
from django.conf import settings
from django.contrib.auth.models import User
from django.core.cache import cache
from django.db.models import signals
from django.db.models.aggregates import Count
from pymongo import ASCENDING, DESCENDING
from time import time
from yabase.models import Radio, SongMetadata, SongInstance
from yacore.database import queryset_iterator
from yaref.models import YasoundSong
from yasearch.task import async_add_song, async_remove_song, \
    async_add_radio, async_remove_radio
import indexer
import indexer as yasearch_indexer
import logging
import settings as yasearch_settings
import utils as yasearch_utils
import string


LOCK_EXPIRE = 60 * 10  # Lock expires in 10 minutes

logger = logging.getLogger("yaapp.yaref")


def build_mongodb_index(upsert=False, erase=False, skip_songs=False):
    """
    build mongodb fuzzy index : if upsert=False then document is inserted without checking for existent one
    """
    lock_id = "build-mongo-db-index-lock"
    acquire_lock = lambda: cache.add(lock_id, "true", LOCK_EXPIRE)
    release_lock = lambda: cache.delete(lock_id)
    if not acquire_lock():
        logger.info('build_mongodb_index locked')
        return

    if erase:
        logger.info("deleting index")
        indexer.erase_index(skip_songs=skip_songs)

    if upsert:
        logger.info("using upsert")
    else:
        logger.info("not using upsert")

#
#    YasoundSong
#
    if not skip_songs:
        songs = YasoundSong.objects.all()
        last_indexed = YasoundSong.objects.last_indexed()
        if last_indexed:
            logger.info("last indexed song = %d" % (last_indexed.id))
            songs = songs.filter(id__gt=last_indexed.id)
        count = songs.count()
        logger.info("processing %d songs" % (count))
        if count > 0:
            start = time()
            if upsert:
                for i, song in enumerate(queryset_iterator(songs)):
                    song.build_fuzzy_index(upsert=True)
                    if i % 10000 == 0 and i != 0:
                        elapsed = time() - start
                        logger.info("processed %d/%d (%d%%) songs in %s seconds" % (i + 1, count, 100 * i / count, str(elapsed)))
                        start = time()
            else:
                bulk = indexer.begin_bulk_insert()
                for i, song in enumerate(queryset_iterator(songs)):
                    bulk.append(song.build_fuzzy_index(upsert=False, insert=False))
                    if i % 10000 == 0 and i != 0:
                        indexer.commit_bulk_insert_songs(bulk)
                        bulk = indexer.begin_bulk_insert()
                        elapsed = time() - start
                        logger.info("processed %d/%d (%d%%) songs in % seconds" % (i + 1, count, 100 * i / count, str(elapsed)))
                        start = time()
                indexer.commit_bulk_insert_songs(bulk)
                elapsed = time() - start
                logger.info("processed %d/%d (%d%%) songs in % seconds" % (count, count, 100, str(elapsed)))

#
#    Radio
#
    rm = RadiosManager()
    radios = Radio.objects.all()
    last_indexed = Radio.objects.last_indexed()
    if last_indexed:
        logger.info("last indexed radio = %d" % (last_indexed.id))
        radios = radios.filter(id__gt=last_indexed.id)
    count = radios.count()
    logger.info("processing %d radios" % (count))
    if count > 0:
        start = time()
        if upsert:
            for i, radio in enumerate(queryset_iterator(radios)):
                radio.build_fuzzy_index(upsert=True)
                if i % 10000 == 0 and i != 0:
                    elapsed = time() - start
                    logger.info("processed %d/%d (%d%%) radios in %s seconds" % (i + 1, count, 100 * i / count, str(elapsed)))
                    start = time()
        else:
            bulk = rm.begin_bulk_insert()
            for i, radio in enumerate(queryset_iterator(radios)):
                bulk.append(radio.build_fuzzy_index(upsert=False, insert=False))
                if i % 10000 == 0 and i != 0:
                    rm.commit_bulk_insert(bulk)
                    bulk = rm.begin_bulk_insert()
                    elapsed = time() - start
                    logger.info("processed %d/%d (%d%%) radios in % seconds" % (i + 1, count, 100 * i / count, str(elapsed)))
                    start = time()
            rm.commit_bulk_insert(bulk)
            elapsed = time() - start
            logger.info("processed %d/%d (%d%%) radios in % seconds" % (count, count, 100, str(elapsed)))

#
#    User
#
    users = User.objects.filter(userprofile__isnull=False)
#    last_indexed = UserProfile.objects.last_indexed_user()
    doc = yasearch_indexer.get_last_user_doc()
    last_indexed = None
    if doc and doc.count() > 0:
        last_indexed = User.objects.get(id=doc[0]['db_id'])

    if last_indexed:
        logger.info("last indexed user = %d" % (last_indexed.id))
        users = users.filter(id__gt=last_indexed.id, userprofile__isnull=False)
    count = users.count()
    logger.info("processing %d users" % (count))
    if count > 0:
        start = time()
        if upsert:
            for i, user in enumerate(queryset_iterator(users)):
                user.userprofile.build_fuzzy_index(upsert=True)
                if i % 10000 == 0 and i != 0:
                    elapsed = time() - start
                    logger.info("processed %d/%d (%d%%) users in %s seconds" % (i + 1, count, 100 * i / count, str(elapsed)))
                    start = time()
        else:
            bulk = indexer.begin_bulk_insert()
            for i, user in enumerate(queryset_iterator(users)):
                bulk.append(user.get_profile().build_fuzzy_index(upsert=False, insert=False))
                if i % 10000 == 0 and i != 0:
                    indexer.commit_bulk_insert_users(bulk)
                    bulk = indexer.begin_bulk_insert()
                    elapsed = time() - start
                    logger.info("processed %d/%d (%d%%) users in % seconds" % (i + 1, count, 100 * i / count, str(elapsed)))
                    start = time()
            indexer.commit_bulk_insert_users(bulk)
            elapsed = time() - start
            logger.info("processed %d/%d (%d%%) users in % seconds" % (count, count, 100, str(elapsed)))

    logger.info("building mongodb index")

    if not skip_songs:
        indexer.build_index_songs()
    indexer.build_index_users()

    release_lock()
    logger.info("done")


def search_radio_by_user(search_text, user_min_score=50, ready_radios_only=True, radios_with_creator_only=True):
    user_results = UserProfile.objects.search_user_fuzzy(search_text, 5)
    users = []
    for u in user_results:
        user_id = u[0]["db_id"]
        score = u[1]
        if score >= user_min_score:
            users.append(User.objects.get(id=user_id))
        else:
            break
    radios = []
    for u in users:
        user_radios = u.get_profile().own_radios(only_ready_radios=ready_radios_only)
        for r in user_radios:
            if r.creator or not radios_with_creator_only:
                radios.append(r)
    return radios


def search_radio_by_song(search_text, limit=10, ready_radios_only=True, radios_with_creator_only=True):
    song_results = YasoundSong.objects.search_fuzzy(search_text, 1000)
    songs = []
    for s in song_results:
        songs.append(s[0]["db_id"])
    radio_queryset = Radio.objects
    if ready_radios_only:
        radio_queryset = radio_queryset.filter(ready=True)
    if radios_with_creator_only:
        radio_queryset = radio_queryset.filter(creator__isnull=False)
    radios = radio_queryset.filter(current_song__metadata__yasound_song_id__in=songs).order_by('-overall_listening_time')[:limit]
    return radios


class RadiosManager():
    """Store radio information for upload matching & search
    """

    BOOST_SONG = 1.2

    def __init__(self):
        self.db = settings.MONGO_DB
        self.collection = self.db.radios
        self.collection.ensure_index("db_id")
        self.collection.ensure_index("name_dms")
        self.collection.ensure_index("genre_dms")
        self.collection.ensure_index("tags_dms")
        self.collection.ensure_index("all_dms")
        self.collection.ensure_index("song.all")

    def drop(self):
        self.collection.drop()

    def add_radio(self, radio, upsert=False, insert=True):
        name_dms = yasearch_utils.build_dms(unicode(radio), True)
        genre_dms = yasearch_utils.build_dms(radio.genre, True)
        tags_dms = yasearch_utils.build_dms(radio.tags_to_string(), True)

        all_dms = []
        all_dms.extend(name_dms)
        all_dms.extend(genre_dms)
        all_dms.extend(tags_dms)
        all_dms = list(set(all_dms))

        song_instance = None
        try:
            song_instance = radio.current_song
        except SongInstance.DoesNotExist:
            pass

        song_dict = None
        if song_instance:
            song_description = song_instance.song_description(include_cover=False, info_from_yasound_db=True)
            if song_description is not None:
                name_simplified = yasearch_utils.get_simplified_name(song_description.get('name'))
                artist_simplified = yasearch_utils.get_simplified_name(song_description.get('artist'))
                album_simplified = yasearch_utils.get_simplified_name(song_description.get('album'))

                song_all = []
                if name_simplified:
                    song_all.extend(name_simplified.split(' '))
                if artist_simplified:
                    song_all.extend(artist_simplified.split(' '))
                if album_simplified:
                    song_all.extend(album_simplified.split(' '))
                if len(song_all) > 0:
                    song_all = list(set(sorted(song_all)))
                    song_dict = {
                        'all': song_all
                    }

        radio_doc = {
            "db_id": radio.id,
            "name": radio.name,
            "genre": radio.genre,
            "tags": radio.tags_to_string(),

            "name_dms": name_dms,
            "genre_dms": genre_dms,
            "tags_dms": tags_dms,
            "all_dms": all_dms,
            "song": song_dict
        }
        if upsert:
            self.collection.update({"db_id": radio.id}, {"$set": radio_doc}, upsert=True, safe=True)
        elif insert:
            self.collection.insert(radio_doc, safe=True)
        return radio_doc

    def remove_radio(self, radio):
        doc = self.collection.find_one({"db_id": radio.id})
        if doc is not None:
            self.collection.remove({'_id': doc['_id']})

    def _find_docs(self, query, remove_common_words=True):
        dms_search = yasearch_utils.build_dms(query, remove_common_words)
        if not query or len(dms_search) == 0:
            return []

        options = {
            "db_id": True,
            "name": True,
            "genre": True,
            "tags": True,
            "song": True,
        }

        query = query.lower()
        song_search = yasearch_utils.get_simplified_name(query).split(' ')
        query_song = {'song.all': {'$all': song_search}}
        query_radio = {"all_dms": {"$all": dms_search}}

        final_query = {'$or': [
            query_radio,
            query_song
        ]
        }

        res = self.collection.find(final_query, options)
        return res

    def _score_song(self, query, doc, min_score):
        matched = False
        ratio = 0.0
        song = doc.get('song')
        if song is None:
            return matched, ratio
        if song.get('all') is None:
            return matched, ratio

        items = query.split(' ')
        sorted_query = ' '.join(sorted(items))

        ratio = yasearch_utils.token_set_ratio(sorted_query.lower(), ' '.join(song.get('all')), method='mean')
        ratio = ratio * RadiosManager.BOOST_SONG
        if min_score is not None and ratio < min_score:
            matched = False
        else:
            matched = True

        return matched, ratio

    def _score_result(self, query, docs, limit=10, min_score=None):
        results = []
        for r in docs:
            matched, ratio = self._score_song(query, r, min_score=min_score)
            if matched:
                res = (r, ratio)
                results.append(res)
                continue

            radio_info_list = []
            if r["name"] is not None:
                radio_info_list.append(r["name"])
            if r["genre"] is not None:
                radio_info_list.append(r["genre"])
            if r["tags"] is not None:
                radio_info_list.append(r["tags"])
            radio_info = string.join(radio_info_list)
            ratio = yasearch_utils.token_set_ratio(query.lower(), radio_info.lower(), method='mean')
            if min_score is not None and ratio < min_score:
                continue
            res = (r, ratio)
            results.append(res)

        sorted_results = sorted(results, key=lambda i: i[1], reverse=True)
        return sorted_results[:limit]

    def search(self, query, min_score=None, limit=10):
        """search radio, result is ordered with current song first
        """

        docs = self._find_docs(query)
        docs = self._score_result(query, docs, limit=limit, min_score=min_score)
        radios = []
        for r in docs:
            try:
                radio = Radio.objects.get(id=r[0]['db_id'])
                radios.append(radio)
            except Radio.DoesNotExist:
                pass
        return radios

    def search_by_current_song(self, query, min_score=None, limit=10):
        """search radio by current song only
        """

        dms_search = yasearch_utils.build_dms(query, remove_common_words=False)
        if not query or len(dms_search) == 0:
            return []

        options = {
            "db_id": True,
            "name": True,
            "genre": True,
            "tags": True,
            "song": True,
        }

        query = query.lower()
        song_search = yasearch_utils.get_simplified_name(query).split(' ')
        query_song = {'song.all': {'$all': song_search}}
        docs = self.collection.find(query_song, options)
        docs = self._score_result(query, docs, limit=limit, min_score=min_score)
        radios = [Radio.objects.get(id=r[0]['db_id']) for r in docs]
        return radios

    def last_doc(self):
        try:
            return self.collection.find().sort([("db_id", DESCENDING)]).limit(1)[0]
        except:
            return None

    def begin_bulk_insert(self):
        return []

    def commit_bulk_insert(self, data):
        if len(data) > 0:
            self.collection.insert(data, safe=True)


class MostPopularSongsManager():
    def __init__(self):
        self.max_size = settings.MOST_POPULAR_SONG_COLLECTION_SIZE
        self.db = settings.MONGO_DB
        self.collection = self.db.search.mostpopularsongs
        self.collection.ensure_index([("db_id", ASCENDING), ("songinstance__count", DESCENDING)])
        self.collection.ensure_index("db_id", unique=True)
        self.collection.ensure_index("songinstance__count")
        self.collection.ensure_index("song_dms")
        self.collection.ensure_index("artist_dms")
        self.collection.ensure_index("album_dms")

    def drop(self):
        self.collection.drop()

    def populate(self):
        limit = self.max_size
        qs = SongMetadata.objects.filter(yasound_song_id__isnull=False).annotate(Count('songinstance')).order_by('-songinstance__count')[:limit]

        self.collection.drop()
        for metadata in qs:
            song_dms = yasearch_utils.build_dms(metadata.name, True, yasearch_settings.SONG_STRING_EXCEPTIONS)
            artist_dms = yasearch_utils.build_dms(metadata.artist_name, True, yasearch_settings.SONG_STRING_EXCEPTIONS)
            album_dms = yasearch_utils.build_dms(metadata.album_name, True, yasearch_settings.SONG_STRING_EXCEPTIONS)
            doc = {
                'db_id': metadata.id,
                'yasound_song_id': metadata.yasound_song_id,
                'name': metadata.name,
                'artist': metadata.artist_name,
                'album': metadata.album_name,
                'songinstance__count': metadata.songinstance__count,
                'song_dms': song_dms,
                'artist_dms': artist_dms,
                'album_dms': album_dms
            }
            self.collection.insert(doc, safe=True)

    def remove_song(self, metadata):
        songinstance__count = SongInstance.objects.filter(metadata=metadata).count()
        if songinstance__count <= 1:
            self.delete(metadata.id)
        else:
            self.collection.update({'db_id': metadata.id},
                                   {"$inc": {'songinstance__count': -1}},
                                   safe=True)

    def add_song(self, song_instance):
        doc_count = self.collection.find().count()
        metadata = song_instance.metadata
        if not metadata.yasound_song_id > 0:
            return False

        songinstance__count = SongInstance.objects.filter(metadata=metadata).count()

        docs = self.collection.find().sort('songinstance__count', ASCENDING).limit(1)
        least_popular_doc = None
        try:
            least_popular_doc = docs[0]
        except:
            pass
        if least_popular_doc and least_popular_doc.get('songinstance__count') >= songinstance__count:
            if doc_count >= self.max_size:
                return False

        song_dms = yasearch_utils.build_dms(metadata.name, True, yasearch_settings.SONG_STRING_EXCEPTIONS)
        artist_dms = yasearch_utils.build_dms(metadata.artist_name, True, yasearch_settings.SONG_STRING_EXCEPTIONS)
        album_dms = yasearch_utils.build_dms(metadata.album_name, True, yasearch_settings.SONG_STRING_EXCEPTIONS)
        doc = {
            'db_id': metadata.id,
            'yasound_song_id': metadata.yasound_song_id,
            'name': metadata.name,
            'artist': metadata.artist_name,
            'album': metadata.album_name,
            'songinstance__count': songinstance__count,
            'song_dms': song_dms,
            'artist_dms': artist_dms,
            'album_dms': album_dms
        }
        self.collection.update({"db_id": metadata.id},
                               {"$set": doc}, upsert=True, safe=True)

        doc_count = self.collection.find().count()
        if doc_count > self.max_size:
            if least_popular_doc:
                self.delete(least_popular_doc.get('db_id'))
        return True

    def delete(self, db_id):
        self.collection.remove({'db_id': db_id}, safe=True)

    def all(self, start=0, limit=25):
        docs = self.collection.find().skip(start).limit(limit).sort([('songinstance__count', DESCENDING)])
        return docs

    def find(self, name, artist, album, remove_common_words=True):
        dms_name = yasearch_utils.build_dms(name, remove_common_words)
        dms_artist = yasearch_utils.build_dms(artist, remove_common_words)
        dms_album = yasearch_utils.build_dms(album, remove_common_words)

        query_items = []
        if artist and len(dms_artist) > 0:
            query_items.append({"artist_dms": {"$all": dms_artist}})

        if album and len(dms_album) > 0:
            query_items.append({"album_dms": {"$in": dms_album}})

        if name and len(dms_name) > 0:
            query_items.append({"song_dms": {"$all": dms_name}})

        if len(query_items) == 0:
            return []

        fields = {
            "db_id": True,
            "yasound_song_id": True,
            "name": True,
            "artist": True,
            "album": True,
        }

        res = self.collection.find_one({"$and": query_items}, fields)
        return res


def new_song_instance(sender, instance, created, **kwargs):
    if created:
        async_add_song.delay(instance)


def song_instance_deleted(sender, instance, **kwargs):
    async_remove_song.delay(instance.metadata)


def radio_updated_handler(sender, instance, created, **kwargs):
    logger.info('radio %d has been updated' % (instance.id))
    async_add_radio.delay(instance.id)


def radio_deleted_handler(sender, instance, **kwargs):
    async_remove_radio.delay(instance)


def install_handlers():
    signals.post_save.connect(radio_updated_handler, sender=Radio)
    signals.post_save.connect(new_song_instance, sender=SongInstance)
    signals.pre_delete.connect(song_instance_deleted, sender=SongInstance)
    signals.pre_delete.connect(radio_deleted_handler, sender=Radio)
install_handlers()
