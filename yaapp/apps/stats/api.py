from tastypie.authentication import ApiKeyAuthentication , Authentication
from tastypie.authorization import ReadOnlyAuthorization
from tastypie.resources import ModelResource, ALL
from tastypie import fields
from models import RadioListeningStat
from datetime import datetime, timedelta

class RadioListeningStatResource(ModelResource):
    radio = fields.ForeignKey('yabase.api.RadioResource', 'radio', full=False)
    
    class Meta:
        queryset = RadioListeningStat.objects.all()
        resource_name = 'listening_stats'
        fields = ['date', 'overall_listening_time', 'audience', 'likes', 'dislikes', 'favorites']
        include_resource_uri = False
        authorization= ReadOnlyAuthorization()
        authentication = Authentication()
        allowed_methods = ['get']
        filtering = {
            'radio': ('exact'),
            'date': ('gt'),
        }
        ordering = [
            'date'
        ]
        
    def dispatch(self, request_type, request, **kwargs):
        ref = datetime.now() - timedelta(days=30)
        kwargs['date__gt'] = ref
        return super(RadioListeningStatResource, self).dispatch(request_type, request, **kwargs)
