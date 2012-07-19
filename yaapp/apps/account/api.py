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
import uuid
import time
from yacore.http import fill_app_infos

from django.utils.translation import ugettext_lazy as _

import logging
from yacore.geoip import can_login
logger = logging.getLogger("yaapp.account")




class YasoundApiKeyAuthentication(ApiKeyAuthentication):
    """
    This class allow authentication with 2 ways:
    * standard (ie django web login)
    * api key (handled by tastypie)
      
    See https://github.com/toastdriven/django-tastypie/issues/197 for more info
    """
    
    def is_authenticated(self, request, **kwargs):
        fill_app_infos(request)

        authenticated = False
        if request.user.is_authenticated():
            authenticated = True
        if not authenticated:
            authenticated = super(YasoundApiKeyAuthentication, self).is_authenticated(request, **kwargs)

        if authenticated:
            # inactive users should be kicked out
            if not request.user.is_active:
                return False
            
            userprofile = request.user.userprofile
            userprofile.authenticated()
            
        return authenticated

    def get_identifier(self, request):
        if request.user.is_authenticated():
            return request.user.username
        else:
            return super(YasoundApiKeyAuthentication, self).get_identifier(request)
        
class YasoundPublicAuthentication(YasoundApiKeyAuthentication):
    """
    This class fills request.user if username/apikey info is given
    but authentication is always = True
    """
    
    def is_authenticated(self, request, **kwargs):
        super(YasoundPublicAuthentication, self).is_authenticated(request, **kwargs) # be sure that all extra
        return True
        


class YasoundBasicAuthentication(BasicAuthentication):
    def is_authenticated(self, request, **kwargs):
        if not can_login(request):
            return False
        
        fill_app_infos(request)
        
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
        authentication = YasoundApiKeyAuthentication()
        authorization = Authorization()
        allowed_methods = ['get', 'put']


    def dehydrate(self, bundle):
        userID = bundle.data['id'];
        user = User.objects.get(pk=userID)
        userprofile = user.userprofile        
        userprofile.fill_user_bundle(bundle)
        
        own_radio = userprofile.own_radio
        if own_radio and own_radio.ready:
            bundle.data['own_radio'] = own_radio.as_dict()
        current_radio = userprofile.current_radio
        if current_radio and current_radio.ready:
            bundle.data['current_radio'] = current_radio.as_dict()
        
        if bundle.request.user == user:
            userprofile.fill_user_bundle_with_login_infos(bundle)
        
        return bundle
    
    def obj_update(self, bundle, request=None, **kwargs):
        print 'UserResource.obj_update'
        print 'bundle:'
        print bundle
        user_resource = super(UserResource, self).obj_update(bundle, request, **kwargs)
        user = user_resource.obj        
        user_profile = user.userprofile
        user_profile.update_with_bundle(bundle, False)
        return user_resource
    
class PublicUserResource(UserResource):
    """
    This resource is the public version of the user resource : 
    
    * anonymous access allowed
    * access by username instead of id in order to avoid easy guess of our data
    * no private info (facebook_token, ..) even if caller is user
    * last history
    """
    class Meta:
        queryset = User.objects.all()
        resource_name = 'public_user'
        fields = ['id']
        include_resource_uri = False
        authorization = ReadOnlyAuthorization()
        
    def override_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/(?P<username>\S+)/$" % self._meta.resource_name, self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),
        ]
        
    def dehydrate(self, bundle):
        userID = bundle.data['id'];
        user = User.objects.get(pk=userID)
        userprofile = user.userprofile        
        userprofile.fill_user_bundle(bundle)
        
        own_radio = userprofile.own_radio
        if own_radio and own_radio.ready:
            bundle.data['own_radio'] = own_radio.as_dict(full=True)
        current_radio = userprofile.current_radio
        if current_radio and current_radio.ready:
            bundle.data['current_radio'] = current_radio.as_dict(full=True)
        
        userprofile.fill_user_bundle_with_history(bundle)
        
        return bundle
        

class PopularUserResource(UserResource):
    """
    This resource is the "popular" version of the user resource : 
    
    * anonymous access allowed
    * most popular users first
    
    """
    class Meta:
        queryset = UserProfile.objects.popular_users()
        resource_name = 'popular_user'
        fields = ['id']
        include_resource_uri = False
        authorization = ReadOnlyAuthorization()
        
        
def add_api_key_to_bundle(user, bundle):
    k = ApiKey.objects.get(user=user).key
    bundle.data['api_key'] = k
    
    
class SignupAuthentication(Authentication):
    def is_authenticated(self, request, **kwargs):
        print 'signup authentication'
        fill_app_infos(request)
        
        print request.COOKIES
        cookies = request.COOKIES
        if not cookies.has_key(account_settings.APP_KEY_COOKIE_NAME):
            return False
        if cookies[account_settings.APP_KEY_COOKIE_NAME] != account_settings.APP_KEY_IPHONE:
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
        user.username = build_random_username()
        user.set_password(password) # encrypt password
        user.save()
        
        # send confirmation email
        EmailAddress.objects.add_email(user, user.email)
            
        user_profile = user.userprofile
        user_profile.yasound_email = bundle.data['email']
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

        # add social stuff        
        userprofile.fill_user_bundle_with_login_infos(bundle)     
        
        userprofile.logged(bundle.request)
        
        add_api_key_to_bundle(user, bundle)
        return bundle
    
    def apply_authorization_limits(self, request, object_list):
        return object_list.filter(id=request.user.id)
    
 
def build_random_username():
        candidate = uuid.uuid4().hex[:30]
        if User.objects.filter(username=candidate).count() > 0:
            build_random_username()
        return candidate
    
def _download_facebook_profile(token):
    facebook_profile = json.load(urllib.urlopen("https://graph.facebook.com/me?" + urllib.urlencode(dict(access_token=token))))
    if not facebook_profile:
        logger.error('cannot communicate with facebook')
        return None
    
    if facebook_profile.has_key('error'):
        logger.error('cannot communicate with facebook: %s' %(facebook_profile['error']))
        return None
    
    if not facebook_profile.has_key('id'):
        logger.error('no "id" attribute in facebook profile')
        logger.error(facebook_profile)
        return None

    return facebook_profile
        
    
class SocialAuthentication(Authentication):
    def is_authenticated(self, request, **kwargs):
        if not can_login(request):
            return False
        
        authenticated = False
        fill_app_infos(request)
        
        # Application Cookie authentication:
        cookies = request.COOKIES
        if not cookies.has_key(account_settings.APP_KEY_COOKIE_NAME):
            logger.error('no cookies')
            return False
        if cookies[account_settings.APP_KEY_COOKIE_NAME] != account_settings.APP_KEY_IPHONE:
            logger.error('no cookies')
            return False
        # Social account verification:
        ACCOUNT_TYPE_PARAM_NAME = 'account_type'
        UID_PARAM_NAME = 'uid'
        TOKEN_PARAM_NAME = 'token'
        NAME_PARAM_NAME = 'name'
        EMAIL_PARAM_NAME = 'email'
        EXPIRATION_DATE = 'expiration_date'
        
        params = request.GET
        if not (params.has_key(ACCOUNT_TYPE_PARAM_NAME) and params.has_key(UID_PARAM_NAME) and params.has_key(TOKEN_PARAM_NAME) and params.has_key(NAME_PARAM_NAME)):
            logger.error('missing informations')
            return False
        
        account_type = params[ACCOUNT_TYPE_PARAM_NAME]
        uid = params[UID_PARAM_NAME]
        token = params[TOKEN_PARAM_NAME]
        name = params[NAME_PARAM_NAME]
        email = None
        if params.has_key(EMAIL_PARAM_NAME):
            email = params[EMAIL_PARAM_NAME]
            
        expiration_date = params.get(EXPIRATION_DATE)
        
        username = build_random_username()
        if account_type in account_settings.ACCOUNT_TYPES_FACEBOOK:
            logger.debug('account type : facebook')
            
            max_retry = 3
            retry = 0
            while retry < max_retry:
                facebook_profile = _download_facebook_profile(token)
                if facebook_profile is not None:
                    break
                time.sleep(1)
                retry += 1
                
            if not facebook_profile:
                return False
            
            if facebook_profile['id'] != uid:
                logger.error('uid does not match')
                return False
            
            try:
                profile = UserProfile.objects.get(facebook_uid=uid)
                user = profile.user
                profile.add_account_type(account_settings.ACCOUNT_MULT_FACEBOOK, commit=False)
                profile.facebook_token = token
                profile.facebook_username = name
                profile.facebook_email = email
                profile.facebook_expiration_date = expiration_date
                profile.save()
                request.user = user
                authenticated = True
            except UserProfile.DoesNotExist:
                logger.debug('user unknown, creating')
                user = User.objects.create(username=username)
                if email:
                    user.email = email
                    user.save()
                profile = user.userprofile
                profile.facebook_uid = uid
                profile.facebook_token = token
                profile.facebook_username = name
                profile.facebook_email = email
                profile.facebook_expiration_date = expiration_date
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
                logger.info('facebook user created')
                authenticated = True
        elif account_type in account_settings.ACCOUNT_TYPES_TWITTER:            
            TOKEN_SECRET_PARAM_NAME = 'token_secret'
            if not params.has_key(TOKEN_SECRET_PARAM_NAME):
                return False
        
            token_secret = params[TOKEN_SECRET_PARAM_NAME]
            auth = tweepy.OAuthHandler(yaapp_settings.YASOUND_TWITTER_APP_CONSUMER_KEY, yaapp_settings.YASOUND_TWITTER_APP_CONSUMER_SECRET)
            auth.set_access_token(token, token_secret)
            api = tweepy.API(auth)
            res = api.verify_credentials()
            if (not res) or (res == False):
                logger.error('cannot communicate with twitter')
                return False
            if res.id != int(uid):
                logger.error('res id does not match')
                return False
            
            try:
                profile = UserProfile.objects.get(twitter_uid=uid)
                user = profile.user
                profile.add_account_type(account_settings.ACCOUNT_MULT_TWITTER, commit=False)
                profile.twitter_token = token
                profile.twitter_token_secret = token_secret
                profile.twitter_username = name
                profile.twitter_email = email
                profile.save()
                request.user = user
                authenticated = True
            except UserProfile.DoesNotExist:
                user = User.objects.create(username=username)
                if email:
                    user.email = email
                    user.save()
                profile = user.userprofile
                profile.twitter_uid = uid
                profile.twitter_token = token
                profile.twitter_token_secret = token_secret
                profile.twitter_username = name
                profile.twitter_email = email
                profile.add_account_type(account_settings.ACCOUNT_MULT_TWITTER, commit=False)
                profile.name = name
                profile.save()
                profile.scan_friends()
                profile.update_with_social_picture()
                
                request.user = user
                
                radio = Radio.objects.filter(creator=user.id)[0]
                radio.create_name(user)
                authenticated = True
        else:
            return False
        
        if authenticated:
            profile.logged(request)
                
        return authenticated
    
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
        
        # add specific login informations
        # add social stuff   
        userprofile.fill_user_bundle_with_login_infos(bundle)     
        
        add_api_key_to_bundle(user, bundle)
        print 'login social dehydrate OK'
        return bundle

    def apply_authorization_limits(self, request, object_list):
        return object_list.filter(id=request.user.id)
        