from bson.code import Code
from django.conf import settings
from django.db.models import signals
from pymongo import DESCENDING
from yabase.models import SongMetadata, Radio
from yarecommendation.task import async_add_radio
from yarecommendation.utils import top_matches
from yaref.models import YasoundSong, YasoundGenre
from yasearch.utils import get_simplified_name
import logging
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
        return  next_code

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

class ClassifiedRadiosManager():
    def __init__(self):
        self.db = settings.MONGO_DB
        self.collection = self.db.recommendation.radios
        self.collection.ensure_index("db_id")
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
            'db_id' : radio.id,
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
                logger.info('computed %d radios (%d%%)', i+1, 100*(i+1)/count)
            self.add_radio(radio)
        logger.info('computed %d radios (%d%%)', i+1, 100*(i+1)/count)
        logger.info('done')
            
    def calculate_similar_radios(self):
        docs = list(self.all())
        count = len(docs)
        logger.info('%d radios to compute' % (count))
        for i,doc in enumerate(docs):
            if i % 100 == 0:
                logger.info('computed %d radios (%d%%)', i+1, 100*(i+1)/count)
            scores = top_matches(docs, doc, 10)
            self.collection.update({'db_id': doc.get('db_id')}, 
                                   {'$set': {
                                        'similar_radios': scores
                                    }}, 
                                   upsert=True, 
                                   safe=True)
        logger.info('computed %d radios (%d%%)', i+1, 100*(i+1)/count)
        logger.info('done')
        
        
    def _intersect(self, a, b):
        return list(set(a) & set(b))
        
    def _co_occurrences(self, a, b):
        return float(len(self._intersect(a, b)))
    
    def find_similar_radios(self, artists):
        similarities = []
        if len(artists) == 0:
            return similarities
        artists_sanitized = []
        for artist in artists:
            artist_name = get_simplified_name(artist).replace('.', '').replace('$', '')
            artists_sanitized.append(artist_name)
        
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
        similarities = similarities[0:20]
        return similarities 

        
        
    def all(self):
        return self.collection.find()
    
    def radio_doc(self, radio_id):
        return self.collection.find_one({'db_id': radio_id})
    
def new_radio(sender, instance, created, **kwargs):
    if created:
        async_add_radio.apply_async(args=[instance], countdown=60*60)

def install_handlers():
    signals.post_save.connect(new_radio, sender=Radio)
install_handlers()    
    