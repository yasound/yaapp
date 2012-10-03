from django.db import models
from datetime import datetime, timedelta
from dateutil.relativedelta import *


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

        # add missing days
        prev_date = None
        final_result = []
        first = True
        for stat in results:
            if first:
                final_result.append(stat)
                prev_date = stat.date
                first = False
                continue

            if prev_date is None:
                continue
            diff = stat.date - prev_date
            if diff.days >= 1:
                for day in range(1, diff.days):
                    date = prev_date + relativedelta(days=+day)
                    final_result.append(RadioListeningStat(date=date,
                        radio=radio,
                        connections=0,
                        audience_peak=0,
                        overall_listening_time=0,
                        favorites=0,
                        likes=0,
                        dislikes=0))
            final_result.append(stat)
            prev_date = stat.date
        return final_result


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

    def as_dict(self):
        data = {
            'id': self.id,
            'date': self.date,
            'overall_listening_time': self.overall_listening_time,
            'overall_listening_time_minutes': int(self.overall_listening_time / 60.0),
            'audience_peak': self.audience_peak,
            'connections': self.connections,
            'favorites': self.favorites,
            'likes': self.likes,
            'dislikes': self.dislikes,
        }
        return data
