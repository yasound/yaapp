from django.conf import settings
from pymongo import DESCENDING
    
class MatchingErrorsManager():
    def __init__(self):
        self.db = settings.MONGO_DB
        self.matching_errors = self.db.metrics.matching_errors
        self.matching_errors.ensure_index("yasound_song_id", unique=True)
        self.matching_errors.ensure_index("reject_count")
        
    def song_rejected(self, yasound_song):
        self.matching_errors.update({"yasound_song_id": yasound_song.id},
                                   {"$inc": {"reject_count": 1}},
                                   upsert=True)
        
    def reject_count(self, yasound_song):
        objects = self.matching_errors.find({"yasound_song_id": yasound_song.id})
        if objects.count() == 0:
            return 0
        return objects[0]["reject_count"]
    
    
    def all(self, skip=0, limit=25):
        return self.matching_errors.find().sort([('reject_count', DESCENDING)]).skip(skip).limit(limit)
    
    def count(self):
        return self.matching_errors.find().count()