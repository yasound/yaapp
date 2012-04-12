from tastypie.authentication import ApiKeyAuthentication , Authentication
from account.api import YasoundApiKeyAuthentication
from tastypie.authorization import ReadOnlyAuthorization
from tastypie.resources import ModelResource, ALL
from tastypie import fields
from models import RadioListeningStat
from datetime import datetime, timedelta
from django.db.models.aggregates import Max
from yabase.models import Radio

class RadioListeningStatResource(ModelResource):
    radio = fields.ForeignKey('yabase.api.RadioResource', 'radio', full=False)
    
    class Meta:
        queryset = RadioListeningStat.objects.all()
        resource_name = 'listening_stats'
        fields = ['date', 'overall_listening_time', 'audience_peak', 'connections', 'likes', 'dislikes', 'favorites']
        include_resource_uri = False
        authorization= ReadOnlyAuthorization()
        authentication = YasoundApiKeyAuthentication()
        allowed_methods = ['get']
        filtering = {
            'radio': ('exact'),
        }
        ordering = [
            'date'
        ]

    def get_object_list(self, request):
        radio_id = int(request.GET.get('radio', 0))
        try:
            radio = Radio.objects.get(id=radio_id)
        except Radio.DoesNotExist:
            return []
        
        daily_stats = RadioListeningStat.objects.daily_stats(radio, nb_days=30)
        return daily_stats

    def obj_get_list(self, request=None, **kwargs):
        # Filtering disabled for brevity...
        return self.get_object_list(request)
    
    
    

    
    
