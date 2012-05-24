from django.conf import settings
from pymongo import DESCENDING
from yabase import signals as yabase_signals
from yahistory.task import async_add_listen_radio_event
import datetime

class UserHistory():
    ETYPE_LISTEN_RADIO  = 'listen'
    ETYPE_MESSAGE       = 'message'
    ETYPE_LIKE_SONG     = 'like_song'
    
    def __init__(self):
        self.db = settings.MONGO_DB
        self.collection = self.db.history.users
        self.collection.ensure_index("db_id")
        self.collection.ensure_index("date")
    
    def erase_metrics(self):
        self.collection.drop()
        
    def add_event(self, user_id, etype, key, data):
        doc = {
            'db_id': user_id,
            'type': etype,
            'date': datetime.datetime.now(),
        }
        doc[key] = data
        self.collection.insert(doc, safe=True)

    def add_listen_radio_event(self, user_id, radio_uuid):
        data = {
            'uuid': radio_uuid
        }
        self.add_event(user_id, UserHistory.ETYPE_LISTEN_RADIO, 'radio', data)
    
    def history_for_user(self, user_id, start_date=None, end_date=None):
        if end_date is None:
            end_date = datetime.date.now()
        if start_date is None:
            start_date = start_date + datetime.timedelta(days=-1)
        return self.collection.find({'db_id': user_id,
                                      'date': {"$gte": start_date, "$lte": end_date}}).sort([('start_date', DESCENDING)])
    
# event handlers
def user_started_listening_handler(sender, radio, user, **kwargs):
    if not user.is_anonymous():
        async_add_listen_radio_event.delay(user.id, radio.uuid)

def install_handlers():
    yabase_signals.user_started_listening.connect(user_started_listening_handler)
install_handlers()    