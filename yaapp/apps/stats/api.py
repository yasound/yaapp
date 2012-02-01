from tastypie.authentication import ApiKeyAuthentication , Authentication
from tastypie.authorization import ReadOnlyAuthorization
from tastypie.resources import ModelResource, ALL
from tastypie import fields
from models import RadioListeningStat

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
