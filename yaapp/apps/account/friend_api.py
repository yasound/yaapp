from tastypie import fields
from tastypie.resources import ModelResource, Resource
from models import UserProfile
from django.contrib.auth.models import User

from tastypie.authorization import Authorization, ReadOnlyAuthorization
from tastypie.authentication import ApiKeyAuthentication

#from yabase.models import Radio
#from yabase.api import RadioResource

class FriendResource(ModelResource):
    class Meta:
        queryset = User.objects.all()
        resource_name = 'friend'
        fields = ['id']
        include_resource_uri = False
        allowed_methods = ['get']
        authentication = ApiKeyAuthentication()
        authorization = ReadOnlyAuthorization() 
        
    def get_object_list(self, request):
        print request.user
        return super(FriendResource, self).get_object_list(request).filter(pk__in=request.user.userprofile.friends.all())
    
    def dehydrate(self, bundle):
        user = bundle.obj
        bundle.data['username'] = user.username
        userprofile = user.userprofile        
        userprofile.fill_user_bundle(bundle)
        return bundle
    
    