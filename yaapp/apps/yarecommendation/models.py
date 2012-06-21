from django.conf import settings
from pymongo import DESCENDING
from yabase.models import SongMetadata, Radio
from yaref.models import YasoundSong, YasoundGenre


class ClassifiedRadiosManager():
    def __init__(self):
        self.db = settings.MONGO_DB
        self.collection = self.db.recommendation.radios
        self.collection.ensure_index("db_id")
    
    def drop(self):
        self.collection.drop()
    
    def add_radio(self, radio):
        ids = list(SongMetadata.objects.filter(songinstance__playlist__radio=radio).values_list('yasound_song_id', flat=True))
        songs = YasoundSong.objects.filter(id__in=ids)
        
        classification = {}
        for song in songs:
            genres = YasoundGenre.objects.filter(yasoundsonggenre__song=song)
            for genre in genres:
                classification[genre.name_canonical] = classification.get(genre.name_canonical, 0) +1 
        
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
            
    def all(self):
        return self.collection.find()