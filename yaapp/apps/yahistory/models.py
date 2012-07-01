from django.conf import settings
from pymongo import DESCENDING
from yabase import settings as yabase_settings, signals as yabase_signals
from yahistory.task import async_add_listen_radio_event, \
    async_add_post_message_event, async_add_like_song_event, \
    async_add_favorite_radio_event, async_add_not_favorite_radio_event, \
    async_add_share_event, async_add_animator_event
import datetime

class UserHistory():
    ETYPE_LISTEN_RADIO       = 'listen'
    ETYPE_MESSAGE            = 'message'
    ETYPE_LIKE_SONG          = 'like_song'
    ETYPE_FAVORITE_RADIO     = 'favorite_radio'
    ETYPE_NOT_FAVORITE_RADIO = 'not_favorite_radio'
    ETYPE_SHARE              = 'share'
    ETYPE_ANIMATOR           = 'animator'
    
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
    
    def add_post_message_event(self, user_id, radio_uuid, message):
        data = {
            'uuid': radio_uuid,
            'message': message
        }
        self.add_event(user_id, UserHistory.ETYPE_MESSAGE, 'message', data)

    def add_like_song_event(self, user_id, song_id):
        data = {
            'db_id': song_id,
        }
        self.add_event(user_id, UserHistory.ETYPE_LIKE_SONG, 'song', data)

    def add_favorite_radio_event(self, user_id, radio_uuid):
        data = {
            'uuid': radio_uuid,
        }
        self.add_event(user_id, UserHistory.ETYPE_FAVORITE_RADIO, 'radio', data)

    def add_not_favorite_radio_event(self, user_id, radio_uuid):
        data = {
            'uuid': radio_uuid,
        }
        self.add_event(user_id, UserHistory.ETYPE_NOT_FAVORITE_RADIO, 'radio', data)

    def add_share_event(self, user_id, radio_uuid, share_type):
        data = {
            'uuid': radio_uuid,
            'share_type': share_type
        }
        self.add_event(user_id, UserHistory.ETYPE_SHARE, 'radio', data)

    def add_animator_event(self, user_id, radio_uuid):
        data = {
            'uuid': radio_uuid,
        }
        self.add_event(user_id, UserHistory.ETYPE_ANIMATOR, 'radio', data)

    def all(self, user_id=None, start=0, limit=25):
        if user_id:
            print user_id
            docs = self.collection.find({'db_id': user_id}).skip(start).limit(limit).sort([('date', DESCENDING)])
            print docs.count()
        else:
            docs = self.collection.find().skip(start).limit(limit).sort([('date', DESCENDING)])
        return docs
        

    def history_for_user(self, user_id, start_date=None, end_date=None, infinite=False, etype=None):
        query = {'db_id': user_id}
        if not infinite:
            if end_date is None:
                end_date = datetime.date.now()
            if start_date is None:
                start_date = start_date + datetime.timedelta(days=-1)
                
            query['date'] = {"$gte": start_date, "$lte": end_date}
        if etype:
            query['type'] = etype
            
        return self.collection.find(query).sort([('start_date', DESCENDING)])
    
# event handlers
def user_started_listening_handler(sender, radio, user, **kwargs):
    if not user.is_anonymous():
        async_add_listen_radio_event.delay(user.id, radio.uuid)

def new_wall_event_handler(sender, wall_event, **kwargs):
    user = wall_event.user
    if user is None:
        return
    if user.is_anonymous():
        return
    
    we_type = wall_event.type
    if we_type == yabase_settings.EVENT_MESSAGE:
        async_add_post_message_event.delay(user.id, wall_event.radio.uuid, wall_event.text)
        
    elif we_type == yabase_settings.EVENT_LIKE:
        async_add_like_song_event.delay(user.id, wall_event.song.id)

def favorite_radio_handler(sender, radio, user, **kwargs):
    async_add_favorite_radio_event.delay(user.id, radio.uuid)
    
def not_favorite_radio_handler(sender, radio, user, **kwargs):
    async_add_not_favorite_radio_event.delay(user.id, radio.uuid)

def new_share(sender, radio, user, share_type, **kwargs):
    async_add_share_event.delay(user.id, radio.uuid, share_type=share_type)

def new_animator_activity(sender, user, radio, **kwargs):
    if radio is not None:
        async_add_animator_event.delay(user.id, radio.uuid)

def install_handlers():
    yabase_signals.user_started_listening.connect(user_started_listening_handler)
    yabase_signals.new_wall_event.connect(new_wall_event_handler)
    yabase_signals.favorite_radio.connect(favorite_radio_handler)
    yabase_signals.not_favorite_radio.connect(not_favorite_radio_handler)
    yabase_signals.radio_shared.connect(new_share)
    yabase_signals.new_animator_activity.connect(new_animator_activity)
install_handlers()    