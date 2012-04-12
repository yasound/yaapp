from django.db import models
from datetime import datetime, timedelta


class RadioListeningStatManager(models.Manager):
    def daily_stats(self, radio, nb_days=30):
        ref = datetime.now() - timedelta(days=nb_days)
        original_stats = self.filter(date__gt=ref, radio=radio).order_by('date')
        
        results = []
        # create RadioListeningStat for each day, but DON'T SAVE IT !!! it must not be added in the database
        date = None
        daily_stat = None
        for hourly_stat in original_stats: 
            if not date or date.date() != hourly_stat.date.date():
                date = hourly_stat.date
                date = date.replace(hour=0, minute=0, second=0, microsecond=0)
                daily_stat = RadioListeningStat(date=date, radio=hourly_stat.radio, connections=hourly_stat.connections, audience_peak=hourly_stat.audience_peak, overall_listening_time=hourly_stat.overall_listening_time, favorites=hourly_stat.favorites, likes=hourly_stat.likes, dislikes=hourly_stat.dislikes)
                results.append(daily_stat)
            else:
                audience_peak = daily_stat.audience_peak
                if hourly_stat.audience_peak > audience_peak:
                    audience_peak = hourly_stat.audience_peak
                daily_stat.audience_peak = audience_peak
                daily_stat.connections += hourly_stat.connections
                daily_stat.overall_listening_time = hourly_stat.overall_listening_time
                daily_stat.favorite = hourly_stat.favorites
                daily_stat.likes = hourly_stat.likes
                daily_stat.dislikes = hourly_stat.dislikes
        return results
    
    
class RadioListeningStat(models.Model):
    objects = RadioListeningStatManager()
    radio = models.ForeignKey('yabase.Radio')
    date = models.DateTimeField(auto_now_add=True)
    overall_listening_time = models.FloatField()
    audience_peak = models.IntegerField()
    connections = models.IntegerField()
    favorites = models.IntegerField()
    likes = models.IntegerField()
    dislikes = models.IntegerField()
    
    def __unicode__(self):
        return 'stat for %s' % self.radio
    