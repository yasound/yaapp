from django.conf import settings


class JobManager():
    def __init__(self):
        self.db = settings.MONGO_DB
        self.collection = self.db.yaref.job_manager
        self.collection.ensure_index('id', unique=True)

    def inc(self, key, value):
        key = key.replace('.', '').replace('$', '')
        self.collection.update({
            "id": 'counters'
        }, {
            "$inc": {key: value}
        }, upsert=True, safe=True)

    def get(self, key, default=0):
        key = key.replace('.', '').replace('$', '')
        doc = self.collection.find_one({'id': 'counters'})
        if doc:
            return doc.get(key, default)
        else:
            return 0

class SongAdditionalInfosManager():
    def __init__(self):
        self.db = settings.MONGO_DB
        self.collection = self.db.yaref.songs
        self.collection.ensure_index('db_id', unique=True)
        self.collection.ensure_index('playlist', unique=True)

    def erase_informations(self):
        self.collection.drop()

    def add_information(self, song_id, information):
        self.collection.update({'db_id': song_id}, {'$set': information}, upsert=True, safe=True)

    def remove_information(self, song_id, information_key):
        self.collection.update({'db_id': song_id}, {'$unset': {information_key: 1}}, upsert=True, safe=True)

    def information(self, song_id):
        return self.collection.find_one({'db_id': song_id})

    def remove_song(self, song_id):
        self.collection.remove({'db_id': song_id})
