from account.forms import LoginForm, SignupForm, PasswordResetForm, \
    SetPasswordForm
from check_request import check_api_key_Authentication, check_http_method
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator
from django.contrib.messages.api import get_messages
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseForbidden, \
    HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.template.context import RequestContext

from django.views.decorators.csrf import csrf_exempt
from models import User, UserProfile, Device
import datetime
from django.contrib.messages.api import get_messages
from social_auth import __version__ as version
import json
import settings as account_settings

from django.utils.http import base36_to_int
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from models import User, UserProfile
from social_auth import __version__ as version
import datetime
import logging
import json
from django.contrib.auth import login as auth_login
from django.forms.util import ErrorList
from django_mobile import get_flavour
import urllib
from tastypie.http import HttpBadRequest

logger = logging.getLogger("yaapp.account")


PICTURE_FILE_TAG = 'picture'
import settings as account_settings

class DivErrorList(ErrorList):
    def __unicode__(self):
        return self.as_divs()
    def as_divs(self):
        if not self: return u''
        return u'<div class="errorlist">%s</div>' % ''.join([u'<div class="error">%s</div>' % e for e in self])


@csrf_exempt
def set_user_picture(request, user_id):
    if not check_api_key_Authentication(request):
        return HttpResponse(status=401)
    if not check_http_method(request, ['post']):
        return HttpResponse(status=405)
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return HttpResponse('user does not exist')
    
    if not request.FILES.has_key(PICTURE_FILE_TAG):
        return HttpResponse('request does not contain a picture file')
    
    f = request.FILES[PICTURE_FILE_TAG]
    d = datetime.datetime.now()
    filename = unicode(d) + '.png'
    
    user.userprofile.picture.save(filename, f)
    
    res = 'picture OK for user: %s' % unicode(user)
    return HttpResponse(res)

def get_subscription(request):
    if not check_api_key_Authentication(request):
        return HttpResponse(status=401)

    if not check_http_method(request, ['get']):
        return HttpResponse(status=405)
    
    profile = get_object_or_404(UserProfile, user=request.user)
    subscription = profile.subscription
    return HttpResponse(subscription)

def login(request, template_name='account/login.html'):
    next = request.REQUEST.get('next')

    login_form = LoginForm(prefix='login', error_class=DivErrorList)
    signup_form = SignupForm(prefix='signup', error_class=DivErrorList)
    if request.method == "POST":
        action = request.REQUEST.get('action')
        if action == 'login':
            default_redirect_to = getattr(settings, "LOGIN_REDIRECT_URLNAME", None)
            if default_redirect_to:
                default_redirect_to = reverse(default_redirect_to)
            else:
                default_redirect_to = settings.LOGIN_REDIRECT_URL
            redirect_to = request.REQUEST.get("next")
            # light security check -- make sure redirect_to isn't garabage.
            if not redirect_to or "://" in redirect_to or " " in redirect_to:
                redirect_to = default_redirect_to
            login_form = LoginForm(request.POST, prefix='login', error_class=DivErrorList)
            if login_form.login(request):
                messages.success(request, _(u"Successfully logged in as %(username)s.") % {'username': request.user.username})
                return HttpResponseRedirect(redirect_to)
        elif action == 'signup':
            signup_form = SignupForm(request.POST, prefix='signup', error_class=DivErrorList)
            if signup_form.is_valid():
                username, email = signup_form.save()
                messages.info(request, _("Confirmation email sent to %s" % email))
                return render_to_response("account/registered.html", {
                    "username": username,
                    "email": email,
                    'next': next,
                }, context_instance=RequestContext(request))
            
    return render_to_response(template_name, {
        "login_form": login_form,
        "signup_form": signup_form,
        'next': next,
    }, context_instance=RequestContext(request))    
    

def error(request, template_name='account/login_error.html'):
    messages = get_messages(request)
    return render_to_response(template_name, {'version': version,
                                             'messages': messages},
                              RequestContext(request))
    

@csrf_exempt
def send_ios_push_notif_token(request):
    if not check_api_key_Authentication(request):
        return HttpResponse(status=401)

    if not check_http_method(request, ['post']):
        return HttpResponse(status=405)
    
    data = request.POST.keys()[0]
    post_data_dict = json.loads(data)
    device_token = post_data_dict.get('device_token', None)
    device_token_type = post_data_dict.get('device_token_type', None)
    device_uuid = post_data_dict.get('uuid', None)
    if not device_token or not device_token_type:
        return HttpResponse('bad data')
    
    if device_token_type != account_settings.IOS_TOKEN_TYPE_SANDBOX and device_token_type != account_settings.IOS_TOKEN_TYPE_DEVELOPMENT:
        return HttpResponse('bad data')
    
    
    device, created = Device.objects.get_or_create(user=request.user, uuid=device_uuid)
    device.ios_token = device_token
    device.ios_token_type = device_token_type
    device.save()
    device.set_registered_now()
    
    res = 'send_ios_push_notif_token OK'
    return HttpResponse(res)


def get_notifications_preferences(request):
    if not check_api_key_Authentication(request):
        return HttpResponse(status=401)

    if not check_http_method(request, ['get']):
        return HttpResponse(status=405)
    
    user_profile = request.user.userprofile
    res = user_profile.notif_preferences()
    response = json.dumps(res)
    return HttpResponse(response)

@csrf_exempt
def set_notifications_preferences(request):
    if not check_api_key_Authentication(request):
        return HttpResponse(status=401)

    if not check_http_method(request, ['post']):
        return HttpResponse(status=405)
    
    data = request.POST.keys()[0]
    post_data_dict = json.loads(data)
    print post_data_dict
    user_profile = request.user.userprofile
    user_profile.set_notif_preferences(post_data_dict)
    
    res = 'update_notifications_preferences OK'
    return HttpResponse(res)


def _parse_facebook_item(item):
    if 'object' not in item:
        return
    
    object_value = item['object']
    if object_value != 'user':
        return
    
    if 'entry' not in item:
        return
    
    entries = item['entry']
    if type(entries) != type([]):
        entries = [entries]
    for entry in entries:
        if 'uid' in entry:
            uid = entry['uid']
            try:
                logger.debug("looking for info about %s" % (uid))
                user_profile = UserProfile.objects.get(facebook_uid=uid)
                user_profile.update_with_social_data()
            except:
                logger.error("cannot find user profile with given uid: %s" % (uid))
                pass
    
def facebook_update(request):
    if request.method == 'GET':
        logger.debug('received facebook_update verification')
        hub_mode = request.REQUEST.get('hub_mode')
        hub_verify_token = request.REQUEST.get('hub_verify_token')
        hub_challenge = request.REQUEST.get('hub_challenge')
        logger.debug('hub_mode = %s' % (hub_mode))
        logger.debug('hub_verify_token = %s' % (hub_verify_token))
        logger.debug('hub_challenge = %s' % (hub_challenge))
        if hub_mode == 'subscribe' and \
           hub_verify_token == settings.FACEBOOK_REALTIME_VERIFY_TOKEN:
            return HttpResponse(hub_challenge)
        return HttpResponseForbidden()

    elif request.method == 'POST':
        logger.debug('received update from facebook')
        json_data =  json.loads(request.read())
        logger.debug(json_data)
        
        if type(json_data) == type([]):
            for item in json_data:
                _parse_facebook_item(item)
        else:
            _parse_facebook_item(json_data) 
        return HttpResponse("OK")
    
@csrf_protect
def password_reset(request, is_admin_site=False,
                   template_name='account/password_reset_form.html',
                   template_name_mobile='account/password_reset_form_mobile.html',
                   email_template_name='account/password_reset_email.html',
                   password_reset_form=PasswordResetForm,
                   token_generator=default_token_generator,
                   post_reset_redirect=None,
                   from_email=None,
                   current_app=None,
                   extra_context=None):
    if get_flavour() == 'mobile':
        template_name = template_name_mobile
    
    if post_reset_redirect is None:
        post_reset_redirect = reverse('login')
    if request.method == "POST":
        form = password_reset_form(request.POST, error_class=DivErrorList)
        if form.is_valid():
            opts = {
                'use_https': request.is_secure(),
                'token_generator': token_generator,
                'from_email': from_email,
                'email_template_name': email_template_name,
                'request': request,
            }
            if is_admin_site:
                opts = dict(opts, domain_override=request.META['HTTP_HOST'])
            form.save(**opts)
            messages.warning(request, _("An email was sent to you to reset your password."))
            return HttpResponseRedirect(post_reset_redirect)
    else:
        form = password_reset_form()
    context = {
        'form': form,
    }
    context.update(extra_context or {})
    return render_to_response(template_name, context,
                              context_instance=RequestContext(request, current_app=current_app))

# Doesn't need csrf_protect since no-one can guess the URL
@never_cache
def password_reset_confirm(request, uidb36=None, token=None,
                           template_name='account/password_reset_confirm.html',
                           template_name_mobile='account/password_reset_confirm_mobile.html',
                           token_generator=default_token_generator,
                           set_password_form=SetPasswordForm,
                           post_reset_redirect=None,
                           current_app=None, extra_context=None):
    """
    View that checks the hash in a password reset link and presents a
    form for entering a new password.
    """
    assert uidb36 is not None and token is not None # checked by URLconf
    if get_flavour() == 'mobile':
        template_name = template_name_mobile

    if post_reset_redirect is None:
        post_reset_redirect = '/'
    try:
        uid_int = base36_to_int(uidb36)
        user = User.objects.get(id=uid_int)
    except (ValueError, User.DoesNotExist):
        user = None

    if user is not None and token_generator.check_token(user, token):
        validlink = True
        if request.method == 'POST':
            form = set_password_form(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, _("Your password has been successfully reset."))
                user.backend='django.contrib.auth.backends.ModelBackend'
                auth_login(request, user)
                return HttpResponseRedirect(post_reset_redirect)
        else:
            form = set_password_form(None)
    else:
        validlink = False
        form = None
    context = {
        'form': form,
        'validlink': validlink,
    }
    context.update(extra_context or {})
    return render_to_response(template_name, context,
                              context_instance=RequestContext(request, current_app=current_app))
        
        
@csrf_exempt
def associate(request):
    if not check_api_key_Authentication(request):
        return HttpResponse(status=401)
    
    cookies = request.COOKIES
    if not cookies.has_key(account_settings.APP_KEY_COOKIE_NAME):
        return HttpResponse(status=401)
    if cookies[account_settings.APP_KEY_COOKIE_NAME] != account_settings.APP_KEY_IPHONE:
        return HttpResponse(status=401)
    user = request.user
    profile = user.get_profile()
    
    account_type = request.REQUEST.get('account_type')
    if not account_type:
        return HttpBadRequest(_('Account type is missing from request'))
    
    uid = request.REQUEST.get('uid')
    token = request.REQUEST.get('token')
    token_secret = request.REQUEST.get('token_secret')
    email = request.REQUEST.get('email')
    password = request.REQUEST.get('password')

    res = False
    message = _('Unknown error')
    if account_type in account_settings.ACCOUNT_TYPES_FACEBOOK:
        res, message = profile.add_facebook_account(uid, token)
    elif account_type in account_settings.ACCOUNT_TYPES_TWITTER:
        res, message = profile.add_twitter_account(uid, token, token_secret)
    elif account_type in account_settings.ACCOUNT_TYPES_YASOUND:
        res, message = profile.add_yasound_account(email, password)

    if res:
        message = _('OK')
        return HttpResponse(message)
    else:
        return HttpBadRequest(message)


@csrf_exempt
def dissociate(request):
    if not check_api_key_Authentication(request):
        return HttpResponse(status=401)

    cookies = request.COOKIES
    if not cookies.has_key(account_settings.APP_KEY_COOKIE_NAME):
        return HttpResponse(status=401)
    if cookies[account_settings.APP_KEY_COOKIE_NAME] != account_settings.APP_KEY_IPHONE:
        return HttpResponse(status=401)

    user = request.user
    profile = user.get_profile()

    account_type = request.REQUEST.get('account_type')
    if not account_type:
        return HttpBadRequest(_('Account type is missing from request'))
    
    res = False
    message = _('Unknown error')
    if account_type in account_settings.ACCOUNT_TYPES_FACEBOOK:
        res, message = profile.remove_facebook_account()
    elif account_type in account_settings.ACCOUNT_TYPES_TWITTER:
        res, message = profile.remove_twitter_account()
    elif account_type in account_settings.ACCOUNT_TYPES_YASOUND:
        res, message = profile.remove_yasound_account()
        
    if res:
        message = _('OK')
        return HttpResponse(message)
    else:
        return HttpBadRequest(message)
    
    