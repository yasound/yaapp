from django.conf import settings
from django.db.models import signals
from pymongo import DESCENDING
from yabase.models import SongMetadata, Radio
from yarecommendation.task import async_add_radio
from yarecommendation.utils import top_matches
from yaref.models import YasoundSong, YasoundGenre
from yasearch.utils import get_simplified_name


class ClassifiedRadiosManager():
    def __init__(self):
        self.db = settings.MONGO_DB
        self.collection = self.db.recommendation.radios
        self.collection.ensure_index("db_id")
    
    def drop(self):
        self.collection.drop()
    
    def add_radio(self, radio):
        ids = list(SongMetadata.objects.filter(songinstance__playlist__radio=radio).values_list('yasound_song_id', flat=True))
        songs = YasoundSong.objects.filter(id__in=ids).select_related()
        
        classification = {}
        for song in songs:
            genres = YasoundGenre.objects.filter(yasoundsonggenre__song=song)
            for genre in genres:
                genre_name = get_simplified_name(genre.name_canonical)
                classification[genre_name] = classification.get(genre_name, 0) +1 
        if len(classification.keys()) > 0:
            doc = {
                'db_id' : radio.id,
                'classification': classification
            }
            self.collection.update({'db_id': radio.id}, {'$set': doc}, upsert=True, safe=True)
    
    def populate(self):
        radios = Radio.objects.filter(ready=True)
        self.drop()
        for radio in radios:
            self.add_radio(radio)
            
    def calculate_similar_radios(self):
        docs = list(self.all())
        for doc in docs:
            scores = top_matches(docs, doc, 10)
            self.collection.update({'db_id': doc.get('db_id')}, 
                                   {'$set': {
                                        'similar_radios': scores
                                    }}, 
                                   upsert=True, 
                                   safe=True)
        
    def all(self):
        return self.collection.find()
    
def new_radio(sender, instance, created, **kwargs):
    if created:
        async_add_radio.apply_async(args=[instance], countdown=60*60)

def install_handlers():
    signals.post_save.connect(new_radio, sender=Radio)
install_handlers()    
    