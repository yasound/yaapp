from tastypie import fields
from tastypie.resources import ModelResource, Resource
from models import UserProfile
from django.contrib.auth.models import User

from tastypie.authorization import Authorization, ReadOnlyAuthorization
from tastypie.authentication import ApiKeyAuthentication

from yabase.models import Radio
from yabase.api import RadioResource
from api import YasoundApiKeyAuthentication

class FriendResource(ModelResource):
    current_radio = fields.ForeignKey(RadioResource, attribute='current_radio', full=True, null=True)
    own_radio = fields.ForeignKey(RadioResource, attribute='own_radio', full=True, null=True)
    class Meta:
        queryset = UserProfile.objects.all()
        resource_name = 'friend'
        fields = ['name']
        include_resource_uri = False
        allowed_methods = ['get']
        authentication = YasoundApiKeyAuthentication()
        authorization = ReadOnlyAuthorization() 
        
    def get_object_list(self, request):
        return super(FriendResource, self).get_object_list(request).filter(user__id__in=request.user.userprofile.friends.all())
    
    def dehydrate(self, bundle):
        userprofile = bundle.obj
        user = userprofile.user
        bundle.data['id'] = user.id
        bundle.data['username'] = user.username      
        userprofile.fill_user_bundle(bundle)       
        
        return bundle
    
        