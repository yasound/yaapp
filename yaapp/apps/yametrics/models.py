from account.models import UserProfile
from django.contrib.auth.models import User
from yabase import settings as yabase_settings
from yabase.models import Radio, WallEvent, RadioUser
from django.conf import settings
from yabase import signals as yabase_signals


class MetricsManager():
    def __init__(self):
        self.db = settings.MONGO_DB
        
        self.metrics_glob           = self.db.metrics.glob
        self.metrics_radio_hourly   = self.db.metrics.radio.hourly
        self.metrics_radio_daily    = self.db.metrics.radio.daily
        self.metrics_radio_monthly  = self.db.metrics.radio.monthly
        self.metrics_radio_yearly   = self.db.metrics.radio.yearly
        
    def _get_hour_timestamp(self):
        return None
    
    def _get_day_timestamp(self):
        return None
    
    def _get_month_timestamp(self):
        return None

    def _get_year_timestamp(self):
        return None
    
    def _generate_timestamps(self):
        return [self._get_hour_timestamp(),
                self._get_day_timestamp(),
                self._get_month_timestamp(),
                self._get_year_timestamp()]
    
    def inc_global_value(self, key, value):
        collection = self.metrics_glob
        
        timestamps = self._generate_timestamps()
        for timestamp in timestamps:
            collection.update({
                "timestamp": timestamp
            }, {
                "$inc": {key: value}
            }, upsert=True, safe=True)


def user_stopped_listening_handler(radio, user, duration):
    metrics = MetricsManager()
    metrics.inc_global_value('overall_listening_time', duration)
    metrics.inc_radio_value('listening_time, duration')
    
yabase_signals.user_stopped_listening.connect(user_stopped_listening_handler)

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