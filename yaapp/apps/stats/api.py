from tastypie.authentication import ApiKeyAuthentication , Authentication
from tastypie.authorization import ReadOnlyAuthorization
from tastypie.resources import ModelResource, ALL
from tastypie import fields
from models import RadioListeningStat
from datetime import datetime, timedelta
from django.db.models.aggregates import Max
from Foundation import MAX

class RadioListeningStatResource(ModelResource):
    radio = fields.ForeignKey('yabase.api.RadioResource', 'radio', full=False)
    
    class Meta:
        queryset = RadioListeningStat.objects.all()
        resource_name = 'listening_stats'
        fields = ['date', 'overall_listening_time', 'audience_peak', 'connections', 'likes', 'dislikes', 'favorites']
        include_resource_uri = False
        authorization= ReadOnlyAuthorization()
        authentication = Authentication()
        allowed_methods = ['get']
        filtering = {
            'radio': ('exact'),
        }
        ordering = [
            'date'
        ]

    def get_object_list(self, request):
        radio = int(request.GET.get('radio', 0))
        ref = datetime.now() - timedelta(days=30)
        original_stats = super(RadioListeningStatResource, self).get_object_list(request).filter(date__gt=ref)
        if radio > 0:
            original_stats = original_stats.filter(radio=radio)
        original_stats = original_stats.order_by('date')
        
        results = []
        # create RadioListeningStat for each day, but DON'T SAVE IT !!! it must not be added in the database
        date = None
        daily_stat = None
        for hourly_stat in original_stats:
            if date != hourly_stat.date.date:
                date = hourly_stat.date.date
                daily_stat = RadioListeningStat(date=date, radio=hourly_stat.radio, connections=hourly_stat.connections, audience_peak=hourly_stat.audience_peak, overall_listening_time=hourly_stat.overall_listening_time, favorites=hourly_stat.favorites, likes=hourly_stat.likes, dislikes=hourly_stat.dislikes)
                results.append(daily_stat)
            else:
                audience_peak = MAX(daily_stat.audience_peak, hourly_stat.audience_peak)
                daily_stat.audience_peak = audience_peak
                daily_stat.connections += hourly_stat.connections
                daily_stat.overall_listening_time = hourly_stat.overall_listening_time
                daily_stat.favorite = hourly_stat.favorites
                daily_stat.likes = hourly_stat.likes
                daily_stat.dislikes = hourly_stat.dislikes
        return results

    def obj_get_list(self, request=None, **kwargs):
        # Filtering disabled for brevity...
        return self.get_object_list(request)
