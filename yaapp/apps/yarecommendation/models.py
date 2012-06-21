from django.conf import settings
from pymongo import DESCENDING
from yabase.models import SongMetadata
from yaref.models import YasoundSong, YasoundGenre, YasoundSongGenre


class ClassifiedRadiosManager():
    
    def __init__(self):
        self.db = settings.MONGO_DB
        self.collection = self.db.history.users
        self.collection.ensure_index("db_id")
    
    
    def add_radio(self, radio):
        songs = YasoundSong.objects.filter(id__in=SongMetadata.objects.filter(songinstance__playlist__radio=radio))
        for song in songs:
            classification = {}
            genres = YasoundGenre.objects.filter(yasoundsonggenre__song=song)
            for genre in genres:
                classification[genre] = classification.get(genre, 0) +1 
                
        doc = {
            'db_id' : song.id,
            'classification': classification
        }