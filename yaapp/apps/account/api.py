from django.conf import settings as yaapp_settings
from django.conf.urls.defaults import url
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from emailconfirmation.models import EmailAddress
from models import UserProfile
from tastypie import fields
from tastypie.authentication import ApiKeyAuthentication, BasicAuthentication, \
    Authentication
from tastypie.authorization import Authorization, ReadOnlyAuthorization, \
    DjangoAuthorization
from tastypie.models import ApiKey
from tastypie.resources import ModelResource, Resource
from tastypie.serializers import Serializer
from tastypie.utils import trailing_slash
from tastypie.validation import Validation
from yabase.models import Radio
import datetime
import json
import settings as account_settings
import tweepy
import urllib
from django.utils.translation import ugettext_lazy as _

import logging
logger = logging.getLogger("yaapp.account")

APP_KEY_COOKIE_NAME = 'app_key'
APP_KEY_IPHONE = 'yasound_iphone_app'


class YasoundApiKeyAuthentication(ApiKeyAuthentication):
    def is_authenticated(self, request, **kwargs):
        authenticated = super(YasoundApiKeyAuthentication, self).is_authenticated(request, **kwargs)
        if authenticated:
            # inactive users should be kicked out
            if not request.user.is_active:
                return False
            
            userprofile = request.user.userprofile
            userprofile.authenticated()
        return authenticated

class YasoundBasicAuthentication(BasicAuthentication):
    def is_authenticated(self, request, **kwargs):
        authenticated = super(YasoundBasicAuthentication, self).is_authenticated(request, **kwargs)
        if authenticated:
            # inactive users should be kicked out
            if not request.user.is_active:
                return False
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

class SignupValidation(Validation):
    def is_valid(self, bundle, request=None):
        if not bundle.data:
            return {'__all__': _('Empty data')}

        error = u''
            
        email = bundle.data['email']
        username = bundle.data['username']

        if User.objects.filter(email=email).count() > 0:
            error = _('A user already exists with this email')

        if User.objects.filter(username=username).count() > 0:
            error = _('A user already exists with this username')

        if len(error) > 0:
            logger.info(unicode(error))
        return error

class SignupResource(ModelResource):
    class Meta: 
        queryset = User.objects.all()
        resource_name = 'signup'
        include_resource_uri = False
        fields = ['id', 'username', 'last_name', 'password', 'email']
        authentication = SignupAuthentication()
        authorization = Authorization()
        validation = SignupValidation()
        allowed_methods = ['post', 'get']
        
    def obj_create(self, bundle, request=None, **kwargs):
        #test if user already exist

        user_resource = super(SignupResource, self).obj_create(bundle, request, **kwargs)
        
        user = user_resource.obj
        password = bundle.data['password']
        user.set_password(password) # encrypt password
        user.save()
        
        # send confirmation email
        EmailAddress.objects.add_email(user, user.email)
            
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
        authentication = YasoundBasicAuthentication()
        
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
                profile = UserProfile.objects.get(facebook_uid=uid)
                user = profile.user
                profile.add_account_type(account_settings.ACCOUNT_MULT_FACEBOOK, commit=False)
                profile.facebook_token = token
                profile.save()
                request.user = user
                return True
            except UserProfile.DoesNotExist:
                user = User.objects.create(username=username)
                if email:
                    user.email = email
                    user.save()
                profile = user.userprofile
                profile.facebook_uid = uid
                profile.facebook_token = token
                profile.add_account_type(account_settings.ACCOUNT_MULT_FACEBOOK, commit=False)
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
                profile = UserProfile.objects.get(twitter_uid=uid)
                user = profile.user
                profile.add_account_type(account_settings.ACCOUNT_MULT_TWITTER, commit=False)
                profile.twitter_token = token
                profile.save()
                request.user = user
                return True
            except UserProfile.DoesNotExist:
                user = User.objects.create(username=username)
                if email:
                    user.email = email
                    user.save()
                profile = user.userprofile
                profile.twitter_uid = uid
                profile.twitter_token = token
                profile.twitter_token_secret = token_secret
                profile.add_account_type(account_settings.ACCOUNT_MULT_TWITTER, commit=False)
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
        