from django.conf import settings
from django.db.models import signals
from pymongo import DESCENDING
from yabase.models import SongMetadata, Radio
from yarecommendation.task import async_add_radio
from yarecommendation.utils import top_matches
from yasearch.utils import get_simplified_name
import logging
from datetime import datetime, timedelta
import settings as yarecommendation_settings
logger = logging.getLogger("yaapp.yarecommendation")


class MapArtistManager():
    def __init__(self):
        self.db = settings.MONGO_DB
        self.collection = self.db.recommendation.map_artist
        self.collection.ensure_index("code", unique=True)
        self.collection.ensure_index("artist", unique=True)

    def drop(self):
        self.collection.drop()

    def next_code(self):
        next_code = 0
        last_docs = self.collection.find().sort([('code', DESCENDING)]).limit(1)
        if last_docs.count() != 0:
            next_code = last_docs[0].get('code') + 1
        return next_code

    def artist_code(self, artist_name):
        code = None
        doc = self.collection.find_one({'artist': artist_name})
        if doc is None:
            code = self.next_code()
            doc = {
                'code': code,
                'artist': artist_name
            }
            self.collection.insert(doc, safe=True)
        else:
            code = doc.get('code')
        return code

    def artist_name(self, code):
        doc = self.collection.find_one({'code': code})
        if doc:
            return doc.get('artist')
        return None


class ClassifiedRadiosManager():
    def __init__(self):
        self.db = settings.MONGO_DB
        self.collection = self.db.recommendation.radios
        self.collection.ensure_index("db_id", unique=True)
        self.collection.ensure_index("cluster_id", unique=False)

    def drop(self):
        self.collection.drop()

    def add_radio(self, radio):
        ma = MapArtistManager()
        artists = SongMetadata.objects.filter(songinstance__playlist__radio=radio).exclude(artist_name='').values_list('artist_name', flat=True)
        classification = {}
        artist_list = []
        for artist in artists:
            artist_name = get_simplified_name(artist).replace('.', '').replace('$', '')
            artist_code = ma.artist_code(artist_name)
            classification[str(artist_code)] = classification.get(str(artist_code), 0) + 1
            artist_list.append(artist_code)
        doc = {
            'db_id': radio.id,
            'classification': classification,
            'artists': list(set(artist_list))
        }
        self.collection.update({'db_id': radio.id}, {'$set': doc}, upsert=True, safe=True)

    def populate(self):
        radios = Radio.objects.filter(ready=True)
        count = radios.count()
        logger.info('%d radios to compute' % (count))
        for i, radio in enumerate(radios):
            if i % 100 == 0:
                logger.info('computed %d radios (%d%%)', i + 1, 100 * (i + 1) / count)
            self.add_radio(radio)
        logger.info('computed %d radios (%d%%)', i + 1, 100 * (i + 1) / count)
        logger.info('done')

    def calculate_similar_radios(self):
        docs = list(self.all())
        count = len(docs)
        logger.info('%d radios to compute' % (count))
        for i, doc in enumerate(docs):
            if i % 100 == 0:
                logger.info('computed %d radios (%d%%)', i + 1, 100 * (i + 1) / count)
            scores = top_matches(docs, doc, 10)
            self.collection.update({'db_id': doc.get('db_id')},
                                   {'$set': {
                                        'similar_radios': scores
                                    }},
                                   upsert=True,
                                   safe=True)
        logger.info('computed %d radios (%d%%)', i + 1, 100 * (i + 1) / count)
        logger.info('done')

    def _intersect(self, a, b):
        return list(set(a) & set(b))

    def _co_occurrences(self, a, b):
        return float(len(self._intersect(a, b)))

    def find_similar_radios(self, artists, offset=0, limit=20):
        ma = MapArtistManager()
        similarities = []
        if len(artists) == 0:
            return similarities
        artists_sanitized = []
        for artist in artists:
            artist_name = get_simplified_name(artist).replace('.', '').replace('$', '')
            artists_sanitized.append(ma.artist_code(artist_name))

        docs = self.collection.find()
        for doc in docs:
            doc_artists = doc.get('artists')
            if len(doc_artists) == 0:
                continue

            similarity = 0.5 * (self._co_occurrences(artists_sanitized, doc_artists) /
                                self._co_occurrences(artists_sanitized, artists_sanitized) +
                                self._co_occurrences(doc_artists, artists_sanitized) /
                                self._co_occurrences(doc_artists, doc_artists))

            if similarity > 0:
                similarities.append((similarity, doc.get('db_id')))
        similarities.sort()
        similarities.reverse()
        similarities = similarities[offset:(offset + limit)]
        return similarities

    def all(self):
        return self.collection.find()

    def radio_doc(self, radio_id):
        return self.collection.find_one({'db_id': radio_id})


class RadioRecommendationsCache():
    def __init__(self):
        self.db = settings.MONGO_DB
        self.recommendations = self.db.recommendation_cache.recommendations
        self.recommendations.ensure_index("token", unique=True)
        self.recommendations.ensure_index("save_date")
        self.artists = self.db.recommendation_cache.artists
        self.artists.ensure_index("user_id", unique=True)

    def drop(self):
        self.recommendations.drop()
        self.artists.drop()

    def convert_token(self, token):
        internal_token = 'recommendations_%s' % (token)
        return internal_token

    def save_recommendations(self, recommended_radios_ids):
        import uuid
        token = uuid.uuid4().hex
        internal_token = self.convert_token(token)
        doc = {'save_date': datetime.now(),
                'token': internal_token,
                'radio_ids': recommended_radios_ids
        }
        self.recommendations.insert(doc, safe=True)
        return token

    def get_recommendations(self, token):
        internal_token = self.convert_token(token)
        doc = self.recommendations.find_one({'token': internal_token})
        if doc is None:
            return None
        radio_ids = doc['radio_ids']
        return radio_ids

    def clean_deprecated_recommendations(self, recommendation_lifetime=yarecommendation_settings.DEFAULT_RECOMMENDATION_LIFETIME):
        """
        removes all entries older than (now - recommendation_lifetime)
        recommendation_lifetime is in seconds
        """
        date_limit = datetime.now() - timedelta(seconds=recommendation_lifetime)
        self.recommendations.remove({'save_date': {'$lt': date_limit}})

    def save_artists(self, artist_list, user):
        doc = {'user_id': user.id,
                'save_date': datetime.now(),
                'artists': artist_list
        }
        self.artists.update({'user_id': doc['user_id']}, doc, upsert=True)

    def get_artists(self, user):
        artist_list = self.artists.find_one({'user_id': user.id})
        if artist_list is None:
            return None
        return artist_list['artists']


def new_radio(sender, instance, created, **kwargs):
    if created:
        async_add_radio.apply_async(args=[instance], countdown=60 * 60)


def install_handlers():
    signals.post_save.connect(new_radio, sender=Radio)
install_handlers()
