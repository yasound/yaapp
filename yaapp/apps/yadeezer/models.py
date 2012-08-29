from django.conf import settings

class PlaylistManager():
    def __init__(self):
        self.db = settings.MONGO_DB
        self.collection = self.db.deezer.playlists
        self.collection.ensure_index('id', unique=True)

    def add(self, doc):
        self.collection.update({'id': doc.get('id')}, {'$set': doc}, upsert=True, safe=True)


class TrackManager():
    def __init__(self):
        self.db = settings.MONGO_DB
        self.collection = self.db.deezer.tracks
        self.collection.ensure_index('id', unique=True)
        self.collection.ensure_index('playlist')

    def add(self, doc):
        self.collection.update({'id': doc.get('id')}, {'$set': doc}, upsert=True, safe=True)
