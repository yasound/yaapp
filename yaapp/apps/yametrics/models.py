from account.models import UserProfile
from django.conf import settings
from django.contrib.auth.models import User
from yabase import settings as yabase_settings, signals as yabase_signals
from yabase.models import Radio, WallEvent, RadioUser
from django.db.models import signals
import datetime


class MetricsManager():
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

    def get_metrics_for_timestamp(self, timestamp):
        collection = self.metrics_glob
        return collection.find_one({'timestamp': timestamp})
    
def user_stopped_listening_handler(radio, user, duration):
    metrics = MetricsManager()
    metrics.inc_global_value('listening_time', duration)
yabase_signals.user_stopped_listening.connect(user_stopped_listening_handler)

def new_wall_event_handler(wall_event):
    metrics = MetricsManager()
    we_type = wall_event.type
    if we_type == yabase_settings.EVENT_MESSAGE:
        metrics.inc_global_value('new_wall_messages', 1)
    elif we_type == yabase_settings.EVENT_LIKE:
        metrics.inc_global_value('new_song_like', 1)
yabase_signals.new_wall_event.connect(new_wall_event_handler)

def new_user_profile_handler(sender, instance, created, **kwargs):
    if created:
        metrics = MetricsManager()
        metrics.inc_global_value('new_users', 1)
signals.post_save.connect(new_user_profile_handler, sender=UserProfile)

def new_radio_handler(sender, instance, created, **kwargs):
    if created:
        metrics = MetricsManager()
        metrics.inc_global_value('new_radios', 1)
signals.post_save.connect(new_user_profile_handler, sender=UserProfile)


def dislike_radio_handler(radio, user):
    metrics = MetricsManager()
    metrics.inc_global_value('new_radio_dislike', 1)
yabase_signals.dislike_radio.connect(dislike_radio_handler)

def like_radio_handler(radio, user):
    metrics = MetricsManager()
    metrics.inc_global_value('new_radio_like', 1)
yabase_signals.dislike_radio.connect(like_radio_handler)

def neutral_like_radio_handler(radio, user):
    metrics = MetricsManager()
    metrics.inc_global_value('new_radio_neutral_like', 1)
yabase_signals.dislike_radio.connect(neutral_like_radio_handler)


def favorite_radio_handler(radio, user):
    metrics = MetricsManager()
    metrics.inc_global_value('new_favorite_radio', 1)
yabase_signals.favorite_radio.connect(favorite_radio_handler)

def not_favorite_radio_handler(radio, user):
    metrics = MetricsManager()
    metrics.inc_global_value('new_not_favorite_radio', 1)
yabase_signals.favorite_radio.connect(not_favorite_radio_handler)
#def build_daily_metrics():
#    overall_listening_time = Radio.objects.overall_listening_time()
#    yasound_friend_count = UserProfile.objects.yasound_friend_count()
#    user_count = User.objects.filter(is_active=True).count()
#    radio_count = Radio.objects.all().count()        
#    ready_radio_count = Radio.objects.filter(ready=True).count()
#    wall_message_count = WallEvent.objects.filter(type=yabase_settings.EVENT_MESSAGE).count()
#    wall_like_count = WallEvent.objects.filter(type=yabase_settings.EVENT_LIKE).count()
#    favorite_count = RadioUser.objects.filter(favorite=True).count()
        
#    return render_to_response(template_name, {
#        "user_count": User.objects.filter(is_active=True).count(),
#        "radio_count": Radio.objects.all().count(),
#        "ready_radio_count": Radio.objects.filter(ready=True).count(),
#        "wall_message_count": WallEvent.objects.filter(type=yabase_settings.EVENT_MESSAGE).count(),
#        "wall_like_count": WallEvent.objects.filter(type=yabase_settings.EVENT_LIKE).count(),
#        "favorite_count": RadioUser.objects.filter(favorite=True).count(),
#        "yasound_friend_count": UserProfile.objects.all().aggregate(Count('friends'))['friends__count'],
#        "listening_time": overall_listening_time_str,
#        "uploaded_song_count" : YasoundSong.objects.filter(id__gt=2059600).count(),
#        "total_friend_count": total_friend_count
#
#    