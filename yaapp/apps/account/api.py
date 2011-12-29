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
from tastypie.serializers import Serializer

class UserResource(ModelResource):
#    userprofile = fields.OneToOneField('account.api.UserProfileResource', 'userprofile', full=True)
    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'
        fields = ['id', 'username', 'first_name']
        include_resource_uri = False
        list_allowed_methods = ['get', 'put', 'delete']
        detail_allowed_methods = ['get', 'put', 'delete']
#        authentication = ApiKeyAuthentication()
        authentication =    Authentication()
        authorization = Authorization()


    def dehydrate(self, bundle):
        userID = bundle.data['id'];
        user = User.objects.get(pk=userID)
        userprofile = user.userprofile        
        userprofile.fill_user_bundle(bundle)
        
        add_api_key_to_bundle(user, bundle)
        return bundle
    
    
#    def obj_create(self, bundle, request=None, **kwargs):
#        user_resource = super(UserResource, self).obj_create(bundle, request, **kwargs)
#        
#        user = user_resource.obj
#        user_profile = user.userprofile
#        user_profile.update_with_bundle(bundle, True)
#        
#        return user_resource
    
    def obj_update(self, bundle, request=None, **kwargs):
        user_resource = super(UserResource, self).obj_update(bundle, request, **kwargs)
        
        user = user_resource.obj        
        user_profile = user.userprofile
        user_profile.update_with_bundle(bundle, False)
        
        return user_resource
    
    
    
#class UserProfileResource(ModelResource):
#    class Meta:
#        queryset = UserProfile.objects.all()
#        resource_name = 'userprofile'
#        fields = ['id', 'twitter_account', 'facebook_account', 'bio_text']
#        include_resource_uri = False    

#class UserApiKeyResource(ModelResource):
#    class Meta: 
#        queryset = ApiKey.objects.all()
#        resource_name = 'api_key'
#        include_resource_uri = False
#        fields = ['key']
#        authentication = BasicAuthentication()
#    
#    def apply_authorization_limits(self, request, object_list):
#        print request.user
#        return object_list.filter(user=request.user)
    
    
def add_api_key_to_bundle(user, bundle):
    k = ApiKey.objects.get(user=user).key
    bundle.data['api_key'] = k
    
    
class SignupAuthentication(Authentication):
    def is_authenticated(self, request, **kwargs):
        APP_KEY_COOKIE_NAME = 'app_key'
        APP_KEY_IPHONE = 'yasound_iphone_app'
        print 'signup authentication'
        print request.COOKIES
        cookies = request.COOKIES
        if not cookies.has_key(APP_KEY_COOKIE_NAME):
            return False
        if cookies[APP_KEY_COOKIE_NAME] != APP_KEY_IPHONE:
            return False
        return True

class SignupResource(ModelResource):
    class Meta: 
        queryset = User.objects.all()
        resource_name = 'signup'
        include_resource_uri = False
        fields = ['id', 'username', 'last_name', 'password']
        authentication = SignupAuthentication()
        authorization = Authorization()
        list_allowed_methods = ['post']
        detail_allowed_methods = ['post']
        
    def obj_create(self, bundle, request=None, **kwargs):
        user_resource = super(SignupResource, self).obj_create(bundle, request, **kwargs)
        user = user_resource.obj
        user.set_password(user.password) # encrypt password
        user.save()
            
        user_profile = user.userprofile
        user_profile.update_with_bundle(bundle, True)
        
        return user_resource
    
class LoginResource(ModelResource):
    class Meta: 
        queryset = User.objects.all()
        resource_name = 'login'
        include_resource_uri = False
        fields = ['id', 'username']
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']
        authentication = BasicAuthentication()
        
        
    def dehydrate(self, bundle):
        userID = bundle.data['id'];
        user = User.objects.get(pk=userID)
        userprofile = user.userprofile        
        userprofile.fill_user_bundle(bundle)
        
        add_api_key_to_bundle(user, bundle)
        return bundle
    
    def apply_authorization_limits(self, request, object_list):
        print request.user
#        import pdb
#        pdb.set_trace()
        return object_list.filter(id=request.user.id)
    
 
def build_social_username(uid, account_type):
        username = '{0}@{1}'.format(uid, account_type)
        return username   
    
class SocialAuthentication(Authentication):
    def is_authenticated(self, request, **kwargs):
        ACCOUNT_TYPE_PARAM_NAME = 'account_type'
        UID_PARAM_NAME = 'uid'
        TOKEN_PARAM_NAME = 'token'
        NAME_PARAM_NAME = 'name'
        
        ACCOUNT_TYPE_FACEBOOK = 'facebook'
        ACCOUNT_TYPE_TWITTER = 'twitter'
        
        params = request.GET
        if not (params.has_key(ACCOUNT_TYPE_PARAM_NAME) and params.has_key(UID_PARAM_NAME) and params.has_key(TOKEN_PARAM_NAME) and params.has_key(NAME_PARAM_NAME)):
            return False
        
        account_type = params[ACCOUNT_TYPE_PARAM_NAME]
        uid = params[UID_PARAM_NAME]
        token = params[TOKEN_PARAM_NAME]
        name = params[NAME_PARAM_NAME]
        
        username = build_social_username(uid, account_type)
        if account_type == ACCOUNT_TYPE_FACEBOOK:
            account_valid = True #FIXME todo: check if uid/token values are from a valid facebook account
            if not account_valid:
                return False
            try:
                user = User.objects.get(username=username)
                request.user = user
                return True
            except User.DoesNotExist:
                user = User.objects.create(username=username)
                profile = user.userprofile
                profile.facebook_uid = uid
                profile.facebook_token = uid
                profile.account_type = account_type
                profile.name = name
                profile.save()
                request.user = user
                return True
        elif account_type == ACCOUNT_TYPE_TWITTER:
            account_valid = True #FIXME todo: check if uid/token values are from a valid twitter account
            if not account_valid:
                return False
            try:
                user = User.objects.get(username=username)
                request.user
                return True
            except User.DoesNotExist:
                user = User.objects.create(username=username)
                profile = user.userprofile
                profile.twitter_uid = uid
                profile.twitter_token = uid
                profile.account_type = account_type
                profile.name = name
                profile.save()
                request.user = user
                return True
        
        return False
    
class LoginSocialResource(ModelResource):
    class Meta: 
        queryset = User.objects.all()
        resource_name = 'login_social'
        include_resource_uri = False
        fields = ['id', 'username']
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']
        authentication = SocialAuthentication()
        
        
    def dehydrate(self, bundle):
        userID = bundle.data['id'];
        user = User.objects.get(pk=userID)
        userprofile = user.userprofile        
        userprofile.fill_user_bundle(bundle)
        add_api_key_to_bundle(user, bundle)
        return bundle

    def apply_authorization_limits(self, request, object_list):
        print request.user
        return object_list.filter(id=request.user.id)
        