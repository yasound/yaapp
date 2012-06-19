from account import signals as account_signals
from account.models import UserProfile
from bson.code import Code
from bson.objectid import ObjectId
from dateutil import rrule
from django.conf import settings
from django.db.models import Count, signals
from pymongo import DESCENDING
from task import async_inc_global_value, async_inc_radio_value
from yabase import settings as yabase_settings, signals as yabase_signals
from yabase.models import Radio, SongMetadata
from yametrics.task import async_activity, async_check_if_new_listener, \
    async_radio_activity, async_report_abuse
import datetime
import settings as yametrics_settings

class GlobalMetricsManager():
    """
    Helper class to store and retrieve key-value metrics
    """
    def __init__(self):
        self.db = settings.MONGO_DB
        self.metrics_glob = self.db.metrics.glob
        self.metrics_glob.ensure_index("timestamp", unique=True)
        
    def _get_hour_timestamp(self):
        now = datetime.datetime.now()
        return now.strftime('%Y-%m-%d-%H:00')
    
    def _get_day_timestamp(self):
        now = datetime.datetime.now()
        return now.strftime('%Y-%m-%d')
    
    def _get_month_timestamp(self):
        now = datetime.datetime.now()
        return now.strftime('%Y-%m')

    def _get_year_timestamp(self):
        now = datetime.datetime.now()
        return now.strftime('%Y')
    
    def _generate_timestamps(self):
        return [self._get_hour_timestamp(),
                self._get_day_timestamp(),
                self._get_month_timestamp(),
                self._get_year_timestamp()]
    
    def _generate_past_month_timestamps(self, start_date=None):
        if start_date is None:
            start_date = datetime.datetime.now() + datetime.timedelta(weeks=4)
        timestamps = []
        last_month = start_date + datetime.timedelta(weeks=-8)
        for dt in rrule.rrule(rrule.DAILY, dtstart=last_month, until=start_date):
            timestamps.append(dt.strftime('%Y-%m-%d'))
        return timestamps

    def _generate_graph_timestamps(self, start_date=None):
        if start_date is None:
            start_date = datetime.datetime.now()
        timestamps = []
        
        day = start_date + datetime.timedelta(days=-(90-1))
        for dt in rrule.rrule(rrule.DAILY, dtstart=day, until=start_date):
            timestamps.append(dt.strftime('%Y-%m-%d'))

        return timestamps
    
    def _generate_past_year_timestamps(self, start_date=None):
        if start_date is None:
            start_date = datetime.datetime.now() + datetime.timedelta(weeks=4)
        timestamps = []
        last_month = start_date + datetime.timedelta(weeks=-53)
        for dt in rrule.rrule(rrule.MONTHLY, dtstart=last_month, until=start_date):
            timestamps.append(dt.strftime('%Y-%m'))
        return timestamps

    def erase_global_metrics(self):
        self.metrics_glob.drop()
        
    def inc_global_value(self, key, value):
        collection = self.metrics_glob
        
        timestamps = self._generate_timestamps()
        for timestamp in timestamps:
            collection.update({
                "timestamp": timestamp
            }, {
                "$inc": {key: value}
            }, upsert=True, safe=True)

    def set_daily_value(self, key, value):
        collection = self.metrics_glob
        collection.update({
            "timestamp": self._get_day_timestamp()
        }, {
            "$set": {key: value}
        }, upsert=True, safe=True)

    def set_value(self, key, value):
        collection = self.metrics_glob
        timestamps = self._generate_timestamps()
        for timestamp in timestamps:
            collection.update({
                "timestamp": timestamp
            }, {
                "$set": {key: value}
            }, upsert=True, safe=True)

    def get_metrics_for_timestamp(self, timestamp):
        collection = self.metrics_glob
        return collection.find_one({'timestamp': timestamp})
    
    def get_current_metrics(self):
        collection = self.metrics_glob
        timestamps = self._generate_timestamps()
        metrics = []
        for timestamp in timestamps:
            metric = collection.find_one({'timestamp': timestamp})
            if metric:
                metrics.append(metric)
        return metrics
    
    def get_past_month_metrics(self):
        collection = self.metrics_glob
        timestamps = self._generate_past_month_timestamps()
        metrics = []
        for timestamp in timestamps:
            metric = collection.find_one({'timestamp': timestamp})
            if metric:
                metrics.append(metric)
        return metrics
      
    def get_past_year_metrics(self):
        collection = self.metrics_glob
        timestamps = self._generate_past_year_timestamps()
        metrics = []
        for timestamp in timestamps:
            metric = collection.find_one({'timestamp': timestamp})
            if metric:
                metrics.append(metric)
        return metrics    
    
    def get_graph_metrics(self, keys):
        collection = self.metrics_glob
        timestamps = self._generate_graph_timestamps()
        data = [{
            'timestamp': '-90'
        }, {
            'timestamp' : '-15'
        }, {
            'timestamp': '-7'
        }, {
            'timestamp' : '-3'
        }, {
            'timestamp': '-1'
        }]
        
        for item in data:
            for key in keys:
                item[key] = 0
        
        current_timestamp = 0
        for i, timestamp in enumerate(timestamps):
            if i ==  len(timestamps)-15:
                current_timestamp += 1
            if i ==  len(timestamps)-7:
                current_timestamp += 1
            if i ==  len(timestamps)-3:
                current_timestamp += 1
            if i == len(timestamps)-1:
                current_timestamp += 1

            metric = collection.find_one({'timestamp': timestamp})
            if metric:
                for key in keys:
                    if key in metric:
                        value = metric[key]
                        data[current_timestamp][key] = data[current_timestamp][key] + value
        return data    
      
class TopMissingSongsManager():
    def __init__(self):
        self.db = settings.MONGO_DB
        self.topmissingsongs = self.db.metrics.topmissingsongs
        self.topmissingsongs.ensure_index("db_id", unique=True)
        
    def calculate(self, limit=100):
        collection = self.topmissingsongs
        collection.drop()
        qs = SongMetadata.objects.filter(yasound_song_id__isnull=True).annotate(Count('songinstance')).order_by('-songinstance__count')[:limit]
        for metadata in qs:
            doc = {
                'db_id': metadata.id,
                'name': metadata.name,
                'artist_name': metadata.artist_name,
                'album_name': metadata.album_name,
                'songinstance__count': metadata.songinstance__count
            }
            collection.update({"db_id": metadata.id},
                              {"$set": doc}, upsert=True, safe=True)
    def all(self):
        collection = self.topmissingsongs
        docs = collection.find().sort([('songinstance__count', DESCENDING)])
        return docs

class RadioMetricsManager():
    def __init__(self):
        self.db = settings.MONGO_DB
        self.radios = self.db.metrics.radios
        self.radios.ensure_index("db_id", unique=True)
    
    def erase_metrics(self):
        self.radios.drop()
        
    def inc_value(self, radio_id, key, value):
        collection = self.radios
        collection.update({"db_id": radio_id}, 
                          {"$inc": {key: value}}, 
                          upsert=True,
                          safe=True)
    
    def metrics(self, radio_id):
        """
        return metrics for given radio
        """
        collection = self.radios
        metric = collection.find_one({'db_id': radio_id})
        return metric
    
    def filter(self, key='db_id', id_only=True, limit=5):
        collection = self.radios
        if id_only:
            return collection.find({}, {'db_id': True}).sort([(key, DESCENDING)]).limit(limit)
        else:
            return collection.find().sort([(key, DESCENDING)]).limit(limit)

    def reset_daily_popularity(self):
        collection = self.radios
        collection.update({}, {'$set': {'daily_popularity': 0}}, multi=True)
        
        
        
        

class RadioPopularityManager():
    def __init__(self):
        self.db = settings.MONGO_DB
        self.radios = self.db.metrics.radio_popularity
        self.radios.ensure_index("db_id", unique=True)
        self.settings = self.db.metrics.radio_popularity_settings
        self.settings.ensure_index("name", unique=True)
        
        if self.settings.find({'name':yametrics_settings.ACTIVITY_LISTEN}).count() == 0:
            self.settings.insert({'name':yametrics_settings.ACTIVITY_LISTEN,'value':1})
        if self.settings.find({'name':yametrics_settings.ACTIVITY_SONG_LIKE}).count() == 0:
            self.settings.insert({'name':yametrics_settings.ACTIVITY_SONG_LIKE,'value':5})
        if self.settings.find({'name':yametrics_settings.ACTIVITY_WALL_MESSAGE}).count() == 0:
            self.settings.insert({'name':yametrics_settings.ACTIVITY_WALL_MESSAGE,'value':5})
        if self.settings.find({'name':yametrics_settings.ACTIVITY_SHARE}).count() == 0:
            self.settings.insert({'name':yametrics_settings.ACTIVITY_SHARE,'value':8})
        if self.settings.find({'name':yametrics_settings.ACTIVITY_ADD_TO_FAVORITES}).count() == 0:
            self.settings.insert({'name':yametrics_settings.ACTIVITY_ADD_TO_FAVORITES,'value':8})

    def drop(self):
        self.radios.drop()
        
    def drop_settings(self):
        self.settings.drop()
        
    def most_popular(self, limit=10, skip=0, db_only=True):
        collection = self.radios
        if db_only:
            return collection.find({}, {'db_id': True}).sort([('progression', DESCENDING)]).skip(skip).limit(limit)
        else:
            return collection.find().sort([('progression', DESCENDING)]).skip(skip).limit(limit)
            
    def action(self, radio_id, activity_type):
        inc = self.settings.find({'name':activity_type})[0]['value']
            
        collection = self.radios
        collection.update({"db_id": radio_id}, 
                          {"$inc": {'activity': inc}}, 
                          upsert=True,
                          safe=True)
        
        
    def action_score_coeff(self, activity_type):
        factor = self.settings.find({'name':activity_type})[0]['value']
        return factor
    
    def coeff_documents(self):
        docs = self.settings.find()
        return docs
    
    def update_coeff_doc(self, coeff_id, new_doc):
        if isinstance(coeff_id, str) or isinstance(coeff_id, unicode):
            coeff_id = ObjectId(coeff_id)
        new_doc['_id'] = coeff_id
        val = new_doc['value']
        if type(val) is not int:
            return
        if val < 0:
            return
        
        self.settings.update({'_id':coeff_id}, new_doc)
        
    def compute_progression(self):
        collection = self.radios
        collection.remove({'$or': [{'activity': {'$exists': False, }}, {'activity': 0}] })
        
        docs = collection.find()
        for d in docs:
            activity = d['activity']
            last_activity = d.get('last_activity', 0)
            new_progression = activity - last_activity
            last_activity = activity
            activity = 0
            collection.update({'db_id': d['db_id']}, {'$set': {'progression': new_progression, 'activity': activity, 'last-activity': last_activity} })
            
            

        
class UserMetricsManager():
    def __init__(self):
        self.db = settings.MONGO_DB
        self.collection = self.db.metrics.users
        self.collection.ensure_index("db_id", unique=True)
    
    def erase_metrics(self):
        self.collection.drop()
        self.db.metrics.messages_stats.drop()
        self.db.metrics.likes_stats.drop()
        
    def inc_value(self, user_id, key, value):
        self.collection.update({"db_id": user_id}, 
                               {"$inc": {key: value}}, 
                               upsert=True,
                               safe=True)
        
    def set_value(self, user_id, key, value):
        self.collection.update({"db_id": user_id}, 
                               {"$set": {key: value}}, 
                               upsert=True,
                               safe=True)
        
    def get_value(self, user_id, key):
        doc = self.get_doc(user_id)
        try:
            return doc[key]
        except:
            return None
    def get_doc(self, user_id):
        return self.collection.find_one({'db_id': user_id})
    
    def all(self):
        return self.collection.find()
    
    def update_messages_stats(self):
        output = self.db.metrics.messages_stats.name
        
        map_func = Code("""
        function() {
            if (this.wall_message_activity) {
                emit(this.wall_message_activity, 1);
            }
        }
""")
        
        reduce_func = Code("""
        function(key, values) {
            var total = 0;
            for (var i = 0; i < values.length; i++) {
                total += values[i];
            }
            return total;
        }
""")
        self.collection.map_reduce(map_func, reduce_func, output)
    
    def calculate_messages_per_user_mean(self):
        docs = self.db.metrics.messages_stats.find()
        users_messages = 0.0
        user_count = 0.0
        for doc in docs:
            messages = doc['_id']
            users = doc['value']
            users_messages = users_messages + (messages*users)
            user_count = user_count + users
        mean = 0
        if user_count > 0:
            mean = users_messages / user_count
        return mean
    
    def messages_stats(self):
        """
        return docs like :
        
        {'_id':20, 'value': 12} 
        
        which means :
        
        12 users have posted 20 messages
        """
        return self.db.metrics.messages_stats.find()
    
    def update_likes_stats(self):
        output = self.db.metrics.likes_stats.name
        
        map_func = Code("""
        function() {
            if (this.song_like_activity) {
                emit(this.song_like_activity, 1);
            }
        }
""")
        
        reduce_func = Code("""
        function(key, values) {
            var total = 0;
            for (var i = 0; i < values.length; i++) {
                total += values[i];
            }
            return total;
        }
""")
        self.collection.map_reduce(map_func, reduce_func, output)
    
    def calculate_likes_per_user_mean(self):
        docs = self.db.metrics.likes_stats.find()
        users_likes = 0.0
        user_count = 0.0
        for doc in docs:
            likes = doc['_id']
            users = doc['value']
            users_likes = users_likes + (likes*users)
            user_count = user_count + users
        mean = 0
        if user_count > 0:
            mean = users_likes / user_count
        return mean
    
    def likes_stats(self):
        """
        return docs like :
        
        {'_id':20, 'value': 12} 
        
        which means :
        
        12 users have likes 20 songs
        """
        return self.db.metrics.likes_stats.find()    
class TimedMetricsManager():       
    SLOT_24H        = '24h'
    SLOT_3D         = '3d'
    SLOT_7D         = '7d'
    SLOT_15D        = '15d'
    SLOT_30D        = '30d'
    SLOT_90D        = '90d'
    SLOT_90D_MORE   = '90d_more'

    def __init__(self):
        self.db = settings.MONGO_DB
        self.collection = self.db.metrics.timed
        self.collection.ensure_index("type", unique=True)
    
    def erase_metrics(self):
        self.collection.drop()
        
    def inc_value(self, ttype, key, value):
        self.collection.update({"type": ttype}, 
                               {"$inc": {key: value}}, 
                               upsert=True,
                               safe=True)
        
    def set_value(self, ttype, key, value):
        self.collection.update({"type": ttype}, 
                               {"$set": {key: value}}, 
                               upsert=True,
                               safe=True)
        
    def get_value(self, ttype, key):
        doc = self.collection.find_one({'type': ttype})
        try:
            return doc[key]
        except:
            return None

    def all(self):
        return self.collection.find()
        
    def slot(self, days):
        if days < 1:
            return self.SLOT_24H
        elif days in range(1, 3+1):
            return self.SLOT_3D
        elif days in range(4, 7+1):
            return self.SLOT_7D
        elif days in range(8, 15+1):
            return self.SLOT_15D
        elif days in range(16, 30+1):
            return self.SLOT_30D
        elif days in range(31, 90+1):
            return self.SLOT_90D
        else:
            return self.SLOT_90D_MORE


class AbuseManager():       
    def __init__(self):
        self.db = settings.MONGO_DB
        self.collection = self.db.abuse
        self.collection.ensure_index("db_id")
    
    def drop(self):
        self.collection.drop()
        
    def report_abuse(self, sender, wall_event):
        now = datetime.datetime.now()
        doc = {
            'db_id': wall_event.id,
            'date': now,
            'radio': wall_event.radio.id,
            'sender': sender.id,
            'user': wall_event.user.id,
            'text': wall_event.text
        }
        
        self.collection.update({"db_id": wall_event.id}, 
                               doc, 
                               upsert=True,
                               safe=True)   
    
    def delete_abuse(self, wall_event_id):
        self.collection.remove({'db_id': wall_event_id})
        
    def all(self):
        return self.collection.find()
        
        
## Event handlers
def user_started_listening_handler(sender, radio, user, **kwargs):
    if not user.is_anonymous():
        async_activity.delay(user.id, yametrics_settings.ACTIVITY_LISTEN)
        async_check_if_new_listener(user.id)
    async_inc_radio_value.delay(radio.id, 'current_users', 1)
    async_inc_radio_value.delay(radio.id, 'daily_popularity', 1)
    async_radio_activity(radio.id, yametrics_settings.ACTIVITY_LISTEN)

def user_stopped_listening_handler(sender, radio, user, duration, **kwargs):
    async_inc_global_value.delay('listening_time', duration)
    async_inc_global_value.delay('listening_count', 1)

    async_inc_radio_value.delay(radio.id, 'current_users', -1)

def new_wall_event_handler(sender, wall_event, **kwargs):
    we_type = wall_event.type
    if we_type == yabase_settings.EVENT_MESSAGE:
        async_inc_global_value.delay('new_wall_messages', 1)
        
        user = wall_event.user
        if not user.is_anonymous():
            async_activity.delay(user.id, yametrics_settings.ACTIVITY_WALL_MESSAGE, throttle=False)
            
        async_radio_activity(wall_event.radio.id, yametrics_settings.ACTIVITY_WALL_MESSAGE)
        
    elif we_type == yabase_settings.EVENT_LIKE:
        async_inc_global_value.delay('new_song_like', 1)

        user = wall_event.user
        if not user.is_anonymous():
            async_activity.delay(user.id, yametrics_settings.ACTIVITY_SONG_LIKE, throttle=False)
            
        async_radio_activity(wall_event.radio.id, yametrics_settings.ACTIVITY_SONG_LIKE)
    
    async_inc_radio_value.delay(wall_event.radio.id, 'daily_popularity', 1)

def new_user_profile_handler(sender, instance, created, **kwargs):
    if created:
        async_inc_global_value.delay('new_users', 1)

def new_radio_handler(sender, instance, created, **kwargs):
    if created:
        async_inc_global_value.delay('new_radios', 1)

def dislike_radio_handler(sender, radio, user, **kwargs):
    async_inc_global_value.delay('new_radio_dislike', 1)

def like_radio_handler(sender, radio, user, **kwargs):
    async_inc_global_value.delay('new_radio_like', 1)

def neutral_like_radio_handler(sender, radio, user, **kwargs):
    async_inc_global_value.delay('new_radio_neutral_like', 1)

def favorite_radio_handler(sender, radio, user, **kwargs):
    async_inc_global_value.delay('new_favorite_radio', 1)
    async_inc_radio_value.delay(radio.id, 'daily_popularity', 1)
    async_radio_activity(radio.id, yametrics_settings.ACTIVITY_ADD_TO_FAVORITES)
    
def not_favorite_radio_handler(sender, radio, user, **kwargs):
    async_inc_global_value.delay('new_not_favorite_radio', 1)

def new_device_registered(sender, user, uuid, ios_token, **kwargs):
    if len(ios_token) > 0:
        async_inc_global_value.delay('device_notifications_activated', 1)
    else:
        async_inc_global_value.delay('device_notifications_disabled', 1)

def new_animator_activity(sender, user, radio, **kwargs):
    async_activity.delay(user.id, yametrics_settings.ACTIVITY_ANIMATOR)
    async_inc_global_value.delay('new_animator_activity', 1)

def new_moderator_del_msg_activity(sender, user, **kwargs):
    async_activity.delay(user.id, yametrics_settings.ACTIVITY_MODERATOR_DEL_MSG, throttle=False)
    async_inc_global_value.delay('new_moderator_del_msg_activity', 1)

def new_moderator_abuse_msg_activity(sender, user, wall_event, **kwargs):
    async_activity.delay(user.id, yametrics_settings.ACTIVITY_MODERATOR_ABUSE_MSG, throttle=False)
    async_inc_global_value.delay('new_moderator_abuse_msg_activity', 1)
    async_report_abuse.delay(user, wall_event)
    
    
def new_share(sender, radio, user, share_type, **kwargs):
    
    activity_key = 'share_%s_activity' % (share_type)
    async_activity.delay(user.id, activity_key, throttle=False)
    async_activity.delay(user.id, yametrics_settings.ACTIVITY_SHARE, throttle=False)
    
    async_inc_global_value.delay('new_share', 1)
    key = 'new_share_%s' % (str(share_type))
    async_inc_global_value.delay(key, 1)
    
    async_radio_activity(radio.id, yametrics_settings.ACTIVITY_SHARE)

def install_handlers():
    yabase_signals.user_started_listening.connect(user_started_listening_handler)
    yabase_signals.user_stopped_listening.connect(user_stopped_listening_handler)
    yabase_signals.new_wall_event.connect(new_wall_event_handler)
    signals.post_save.connect(new_user_profile_handler, sender=UserProfile)
    signals.post_save.connect(new_radio_handler, sender=Radio)
    yabase_signals.dislike_radio.connect(dislike_radio_handler)
    yabase_signals.dislike_radio.connect(like_radio_handler)
    yabase_signals.dislike_radio.connect(neutral_like_radio_handler)
    yabase_signals.favorite_radio.connect(favorite_radio_handler)
    yabase_signals.not_favorite_radio.connect(not_favorite_radio_handler)
    yabase_signals.new_animator_activity.connect(new_animator_activity)
    yabase_signals.new_moderator_del_msg_activity.connect(new_moderator_del_msg_activity)
    yabase_signals.new_moderator_abuse_msg_activity.connect(new_moderator_abuse_msg_activity)
    yabase_signals.radio_shared.connect(new_share)
    account_signals.new_device_registered.connect(new_device_registered)
    
install_handlers()
