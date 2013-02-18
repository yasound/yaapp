from django.conf import settings
import datetime
from bson.objectid import ObjectId


class JingleManager():
    """ Store jingles.

    A jingle is::

        jingle = {
            'radio_uuid': radio_uuid,
            'creator': user_id,
            'created': '',
            'updated': '',
            'filename': 'aabbccdd.mp3',
            'name': 'Jingle introduction',
            'description': ''
            'schedule': [{
                'type': 'between_songs',
                'value': 4
            }, {
                'type': 'periodic',
                value: '12h30'
            }, {
                'type': 'periodic',
                value: '18h30'
            }]
        }
    """

    def __init__(self):
        self.db = settings.MONGO_DB
        self.collection = self.db.jingles
        self.collection.ensure_index("radio_uuid")

    def jingles_for_radio(self, radio_uuid):
        return self.collection.find({'radio_uuid': radio_uuid})

    def delete_jingle(self, jingle_id):
        if isinstance(jingle_id, str) or isinstance(jingle_id, unicode):
            jingle_id = ObjectId(jingle_id)
        self.collection.remove({'_id': jingle_id}, safe=True)

    def jingle(self, jingle_id):
        if isinstance(jingle_id, str) or isinstance(jingle_id, unicode):
            jingle_id = ObjectId(jingle_id)
        return self.collection.find_one({'_id': jingle_id})

    def update_jingle(self, doc):
        self.collection.save(doc, safe=True)

    def create_jingle(self, name, radio, creator, description=None, filename=None, schedule=None):
        doc = {
            'radio_uuid': radio.uuid,
            'creator': creator.id,
            'filename': filename,
            'created': datetime.datetime.now(),
            'updated': datetime.datetime.now(),
            'name': name,
            'description': description,
            'schedule': schedule
        }
        return self.collection.insert(doc, safe=True)
