from tastypie import fields
from tastypie.resources import ModelResource, Resource
from models import UserProfile
from django.contrib.auth.models import User
from django.conf.urls.defaults import url
from django.shortcuts import get_object_or_404
from tastypie.utils import trailing_slash
import datetime
from tastypie.authentication import Authentication
from tastypie.authorization import Authorization
from tastypie.authentication import ApiKeyAuthentication , BasicAuthentication
from tastypie.models import ApiKey

class UserResource(ModelResource):
#    userprofile = fields.OneToOneField('account.api.UserProfileResource', 'userprofile', full=True)
    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'
        fields = ['id', 'username']
        include_resource_uri = False
#        authentication = ApiKeyAuthentication()
        authentication = Authentication()
        authorization = Authorization()


    def dehydrate(self, bundle):
        userID = bundle.data['id'];
        userprofile = User.objects.get(pk=userID).userprofile
        
        picture = userprofile.picture
        picture = '/media/' + unicode(picture)
        
        bio = userprofile.bio_text
        facebook_account = userprofile.facebook_account
        twitter_account = userprofile.twitter_account
        url = userprofile.url
        
        bundle.data['picture'] = picture
        bundle.data['bio_text'] = bio
        bundle.data['facebook_account'] = facebook_account
        bundle.data['twitter_account'] = twitter_account
        bundle.data['url'] = url
        return bundle
    
    def updateUserProfile(self, user_profile, bundle):
        user_profile.bio_text = bundle.data['bio_text']
        user_profile.facebook_account = bundle.data['facebook_account']
        user_profile.twitter_account = bundle.data['twitter_account']
        user_profile.save()
    
    def obj_create(self, bundle, request=None, **kwargs):
        user_resource = super(UserResource, self).obj_create(bundle, request, **kwargs)
        
        user = user_resource.obj
        user_profile = user.userprofile
        self.updateUserProfile(user_profile, bundle)
        
        return user_resource
    
    
    
#class UserProfileResource(ModelResource):
#    class Meta:
#        queryset = UserProfile.objects.all()
#        resource_name = 'userprofile'
#        fields = ['id', 'twitter_account', 'facebook_account', 'bio_text']
#        include_resource_uri = False    
    

class UserApiKeyResource(ModelResource):
    class Meta: 
        queryset = ApiKey.objects.all()
        resource_name = 'api_key'
        include_resource_uri = False
        fields = ['key']
        authentication = BasicAuthentication()
    
    def apply_authorization_limits(self, request, object_list):
        print request.user
        return object_list.filter(user=request.user)
        