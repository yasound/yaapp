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

class ClassifiedRadiosManager():
    def __init__(self):
        self.db = settings.MONGO_DB
        self.collection = self.db.recommendation.radios
        self.collection.ensure_index("db_id")
    
    def drop(self):
        self.collection.drop()
    
    def add_radio(self, radio):
        artists = SongMetadata.objects.filter(songinstance__playlist__radio=radio).exclude(artist_name='').values_list('artist_name', flat=True)
        classification = {}
        artist_list = []
        for artist in artists:
            artist_name = get_simplified_name(artist).replace('.', '').replace('$', '')
            classification[artist_name] = classification.get(artist_name, 0) + 1
            artist_list.append(artist_name)
        doc = {
            'db_id' : radio.id,
            'classification': classification,
            'artists': list(set(artist_list))
        }
        self.collection.update({'db_id': radio.id}, {'$set': doc}, upsert=True, safe=True)
    
        ids = list(SongMetadata.objects.filter(songinstance__playlist__radio=radio).values_list('yasound_song_id', flat=True))
        songs = YasoundSong.objects.filter(id__in=ids).select_related()
        genres_ratio = []
        for song in songs:
            genres = YasoundGenre.objects.filter(yasoundsonggenre__song=song)
            for genre in genres:
                genre_name = get_simplified_name(genre.name_canonical).replace('$', '').replace('.', '')
                ratio = (genre_name, 1)
                for existing_ratio in genres_ratio:
                    if existing_ratio[0] == genre_name:
                        genres_ratio.remove(existing_ratio)
                        ratio = (ratio[0], ratio[1] + 1)
                genres_ratio.append(ratio)
        genres_ratio.sort() 
        genres_ratio.reverse()
        limit = genres_ratio[0:5]
        genre_docs = []
        for i,genre in enumerate(limit):
            pos = i
            genre_docs.append({'pos': pos, 'genre': genre[0]})
        doc = {
            'genres': [genre_docs]
        }
        self.collection.update({'db_id': radio.id}, {'$set': doc}, upsert=True, safe=True)
           
    
    def populate(self):
        radios = Radio.objects.filter(ready=True)
        count = radios.count()
        logger.info('%d radios to compute' % (count))
        self.drop()
        for i, radio in enumerate(radios):
            if i % 1000 == 0:
                logger.info('computed %d radios (%d%%)', i+1, 100*(i+1)/count)
            self.add_radio(radio)
        logger.info('computed %d radios (%d%%)', i+1, 100*(i+1)/count)
        logger.info('done')
            
    def calculate_similar_radios(self):
        docs = list(self.all())
        count = len(docs)
        logger.info('%d radios to compute' % (count))
        for i,doc in enumerate(docs):
            if i % 1000 == 0:
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
    
    def find_similar_radios(self, username, artists):
        artists_sanitized = []
        for artist in artists:
            artist_name = get_simplified_name(artist).replace('.', '').replace('$', '')
            artists_sanitized.append(artist_name)
        username_sanitized = get_simplified_name(username).replace('.', '').replace('$', '')
        
        docs = self.collection.find()
        similarities = []
        for doc in docs:
            doc_artists = doc.get('artists')
            if len(doc_artists) == 0:
                continue
            
            similarity = 0.5 * (self._co_occurrences(artists, doc_artists) / 
                                self._co_occurrences(artists, artists) + 
                                self._co_occurrences(doc_artists, artists) / 
                                self._co_occurrences(doc_artists, doc_artists))
            if doc.get('db_id') == 143:
                import pdb
                pdb.set_trace()
            
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
    