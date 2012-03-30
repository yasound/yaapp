from tastypie import fields
from tastypie.resources import ModelResource, Resource
from models import UserProfile
from django.contrib.auth.models import User
from django.conf.urls.defaults import url
from django.shortcuts import get_object_or_404
from tastypie.utils import trailing_slash
import datetime
from tastypie.authentication import Authentication
from tastypie.authorization import Authorization, ReadOnlyAuthorization
from tastypie.authentication import ApiKeyAuthentication , BasicAuthentication
from tastypie.models import ApiKey
from tastypie.serializers import Serializer
from yabase.models import Radio
import settings as account_settings
from django.conf import settings as yaapp_settings
import json
import urllib
import tweepy

APP_KEY_COOKIE_NAME = 'app_key'
APP_KEY_IPHONE = 'yasound_iphone_app'


class YasoundApiKeyAuthentication(ApiKeyAuthentication):
    def is_authenticated(self, request, **kwargs):
        authenticated = super(YasoundApiKeyAuthentication, self).is_authenticated(request, **kwargs)
        if authenticated:
            userprofile = request.user.userprofile
            userprofile.authenticated()
        return authenticated


class UserResource(ModelResource):
    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'
        fields = ['id']
        include_resource_uri = False
        allowed_methods = []
        authentication = YasoundApiKeyAuthentication()
        authorization = ReadOnlyAuthorization()


    def dehydrate(self, bundle):
        userID = bundle.data['id'];
        user = User.objects.get(pk=userID)
        userprofile = user.userprofile        
        userprofile.fill_user_bundle(bundle)
        return bundle
    
    def obj_update(self, bundle, request=None, **kwargs):
        user_resource = super(UserResource, self).obj_update(bundle, request, **kwargs)
        user = user_resource.obj        
        user_profile = user.userprofile
        user_profile.update_with_bundle(bundle, False)
        return user_resource
    
def add_api_key_to_bundle(user, bundle):
    k = ApiKey.objects.get(user=user).key
    bundle.data['api_key'] = k
    
    
class SignupAuthentication(Authentication):
    def is_authenticated(self, request, **kwargs):
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
        allowed_methods = ['post']
        
    def obj_create(self, bundle, request=None, **kwargs):
        #test if user already exist
        user_resource = super(SignupResource, self).obj_create(bundle, request, **kwargs)
        user = user_resource.obj
        user.set_password(user.password) # encrypt password
        
        user.username = bundle.data['name']
        user.email = bundle.data['email']
        user.save()
            
        user_profile = user.userprofile
        user_profile.update_with_bundle(bundle, True)
        
        radio = Radio.objects.filter(creator=user.id)[0]
        radio.create_name(user)
        
        return user_resource
    
class LoginResource(ModelResource):
    class Meta: 
        queryset = User.objects.all()
        resource_name = 'login'
        include_resource_uri = False
        fields = ['id', 'username']
        allowed_methods = ['get']
        authentication = BasicAuthentication()
        
        
    def dehydrate(self, bundle):
        userID = bundle.data['id'];
        user = User.objects.get(pk=userID)
        userprofile = user.userprofile        
        userprofile.fill_user_bundle(bundle)
        
        add_api_key_to_bundle(user, bundle)
        return bundle
    
    def apply_authorization_limits(self, request, object_list):
        return object_list.filter(id=request.user.id)
    
 
def build_social_username(uid, account_type):
        username = '{0}@{1}'.format(uid, account_type)
        return username   
    
class SocialAuthentication(Authentication):
    def is_authenticated(self, request, **kwargs):
        # Application Cookie authentication:
        cookies = request.COOKIES
        if not cookies.has_key(APP_KEY_COOKIE_NAME):
            return False
        if cookies[APP_KEY_COOKIE_NAME] != APP_KEY_IPHONE:
            return False
        
        # Social account verification:
        ACCOUNT_TYPE_PARAM_NAME = 'account_type'
        UID_PARAM_NAME = 'uid'
        TOKEN_PARAM_NAME = 'token'
        NAME_PARAM_NAME = 'name'
        EMAIL_PARAM_NAME = 'email'
        
        params = request.GET
        if not (params.has_key(ACCOUNT_TYPE_PARAM_NAME) and params.has_key(UID_PARAM_NAME) and params.has_key(TOKEN_PARAM_NAME) and params.has_key(NAME_PARAM_NAME)):
            return False
        
        account_type = params[ACCOUNT_TYPE_PARAM_NAME]
        uid = params[UID_PARAM_NAME]
        token = params[TOKEN_PARAM_NAME]
        name = params[NAME_PARAM_NAME]
        email = None
        if params.has_key(EMAIL_PARAM_NAME):
            email = params[EMAIL_PARAM_NAME]
        
        username = build_social_username(uid, account_type)
        if account_type in account_settings.ACCOUNT_TYPES_FACEBOOK:
            facebook_profile = json.load(urllib.urlopen("https://graph.facebook.com/me?" + urllib.urlencode(dict(access_token=token))))
            
            if not facebook_profile:
                return False
            
            if facebook_profile.has_key('error'):
                print facebook_profile['error']
                return False
            
            if not facebook_profile.has_key('id'):
                print 'no "id" attribute in facebook profile'
                return False
            if facebook_profile['id'] != uid:
                print 'uid does not match'
                return False
            
            try:
                user = User.objects.get(username=username)
                profile = user.userprofile
                profile.facebook_token = token
                profile.save()
                request.user = user
                return True
            except User.DoesNotExist:
                user = User.objects.create(username=username)
                if email:
                    user.email = email
                    user.save()
                profile = user.userprofile
                profile.facebook_uid = uid
                profile.facebook_token = token
                profile.account_type = account_type
                profile.name = name
                profile.save()
                
                try:
                    profile.scan_friends()
                except:
                    pass
            
                try:
                    profile.update_with_social_picture()
                except:
                    pass
                
                request.user = user
                
                radio = Radio.objects.filter(creator=user.id)[0]
                radio.create_name(user)
                print 'facebook user created'
                return True
        elif account_type in account_settings.ACCOUNT_TYPES_TWITTER:            
            TOKEN_SECRET_PARAM_NAME = 'token_secret'
            if not params.has_key(TOKEN_SECRET_PARAM_NAME):
                return False
        
            token_secret = params[TOKEN_SECRET_PARAM_NAME]
            auth = tweepy.OAuthHandler(yaapp_settings.YASOUND_TWITTER_APP_CONSUMER_KEY, yaapp_settings.YASOUND_TWITTER_APP_CONSUMER_SECRET)
            auth.set_access_token(token, token_secret)
            api = tweepy.API(auth)
            res = api.verify_credentials()
            print 'verify_credentials:'
            print res
            if (not res) or (res == False):
                return False
            if res.id != int(uid):
                print 'res id does not match'
                return False
            
            try:
                user = User.objects.get(username=username)
                profile = user.userprofile
                profile.twitter_token = token
                profile.save()
                request.user = user
                return True
            except User.DoesNotExist:
                user = User.objects.create(username=username)
                if email:
                    user.email = email
                    user.save()
                profile = user.userprofile
                profile.twitter_uid = uid
                profile.twitter_token = token
                profile.twitter_token_secret = token_secret
                profile.account_type = account_type
                profile.name = name
                profile.save()
                profile.scan_friends()
                profile.update_with_social_picture()
                
                request.user = user
                
                radio = Radio.objects.filter(creator=user.id)[0]
                radio.create_name(user)
                return True
        
        return False
    
class LoginSocialResource(ModelResource):
    class Meta: 
        queryset = User.objects.all()
        resource_name = 'login_social'
        include_resource_uri = False
        fields = ['id', 'username']
        allowed_methods = ['get']
        authentication = SocialAuthentication()
        
        
    def dehydrate(self, bundle):
        userID = bundle.data['id'];
        user = User.objects.get(pk=userID)
        userprofile = user.userprofile        
        userprofile.fill_user_bundle(bundle)
        add_api_key_to_bundle(user, bundle)
        print 'login social dehydrate OK'
        return bundle

    def apply_authorization_limits(self, request, object_list):
        return object_list.filter(id=request.user.id)
        