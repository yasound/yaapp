from account.models import UserProfile
from dateutil import rrule
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import Q, Count, signals
from pymongo import DESCENDING
from task import async_inc_global_value, async_inc_radio_value
from yabase import settings as yabase_settings, signals as yabase_signals
from yabase.models import Radio, WallEvent, RadioUser, SongMetadata
from account import signals as account_signals
import datetime

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
            start_date = datetime.datetime.now() + datetime.timedelta(weeks=4)
        timestamps = []
        
        day = start_date + datetime.timedelta(days=-90)
        timestamps.append(day.strftime('%Y-%m-%d'))

        day = start_date + datetime.timedelta(days=-15)
        timestamps.append(day.strftime('%Y-%m-%d'))

        day = start_date + datetime.timedelta(days=-3)
        timestamps.append(day.strftime('%Y-%m-%d'))

        timestamps.append(start_date.strftime('%Y-%m-%d'))
        return timestamps
    
    def _generate_past_year_timestamps(self, start_date=None):
        if start_date is None:
            start_date = datetime.datetime.now() + datetime.timedelta(weeks=4)
        timestamps = []
        last_month = start_date + datetime.timedelta(weeks=-53)
        for dt in rrule.rrule(rrule.MONTHLY, dtstart=last_month, until=start_date):
            print dt
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
    
    def get_graph_metrics(self):
        collection = self.metrics_glob
        timestamps = self._generate_graph_timestamps()
        metrics = []
        for timestamp in timestamps:
            metric = collection.find_one({'timestamp': timestamp})
            if metric:
                metrics.append(metric)
        return metrics    
      
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
        
        
    
## Event handlers
def user_started_listening_handler(radio, user, **kwargs):
    async_inc_radio_value.delay(radio.id, 'current_users', 1)

def user_stopped_listening_handler(radio, user, duration, **kwargs):
    async_inc_global_value.delay('listening_time', duration)
    async_inc_global_value.delay('listening_count', 1)

    async_inc_radio_value.delay(radio.id, 'current_users', -1)

def new_wall_event_handler(wall_event, **kwargs):
    we_type = wall_event.type
    if we_type == yabase_settings.EVENT_MESSAGE:
        async_inc_global_value.delay('new_wall_messages', 1)
    elif we_type == yabase_settings.EVENT_LIKE:
        async_inc_global_value.delay('new_song_like', 1)

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

def not_favorite_radio_handler(sender, radio, user, **kwargs):
    async_inc_global_value.delay('new_not_favorite_radio', 1)

def new_device_registered(sender, user, uuid, ios_token, **kwargs):
    if len(ios_token) > 0:
        async_inc_global_value.delay('device_notifications_activated', 1)
    else:
        async_inc_global_value.delay('device_notifications_disabled', 1)

def new_animator_activity(user, **kwargs):
    async_inc_global_value.delay('new_animator_activity', 1)

def new_share(radio, user, **kwargs):
    async_inc_global_value.delay('new_share', 1)

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
    yabase_signals.radio_shared.connect(new_share)
    account_signals.new_device_registered.connect(new_device_registered)
    
install_handlers()
