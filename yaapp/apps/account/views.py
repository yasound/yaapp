from check_request import check_api_key_Authentication, check_http_method
from django.conf import settings
from django.contrib.messages.api import get_messages
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render_to_response
from django.template.context import RequestContext
from django.views.decorators.csrf import csrf_exempt
from models import User, UserProfile
from social_auth import __version__ as version
import datetime
import simplejson

import logging
logger = logging.getLogger("yaapp.account")

PICTURE_FILE_TAG = 'picture'

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
    return render_to_response(template_name, {
        'next': next
    }, context_instance=RequestContext(request))    

def error(request, template_name='account/login_error.html'):
    messages = get_messages(request)
    return render_to_response(template_name, {'version': version,
                                             'messages': messages},
                              RequestContext(request))
    
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
        try:
            if request.GET['hub_mode'] == 'subscribe' and \
               request.GET['hub_verify_token'] == settings.FACEBOOK_REALTIME_VERIFY_TOKEN:
                    return HttpResponse(request.GET['hub_challenge'])
        except Exception, _e:
            return HttpResponseForbidden()

    elif request.method == 'POST':
        logger.debug('received update from facebook')
        json_data =  simplejson.loads(request.read())
        logger.debug(json_data)
        
        if type(json_data) == type([]):
            for item in json_data:
                _parse_facebook_item(item)
        else:
            _parse_facebook_item(json_data) 
        return HttpResponse("OK")