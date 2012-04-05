from check_request import check_api_key_Authentication, check_http_method
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.template.context import RequestContext
from django.views.decorators.csrf import csrf_exempt
from models import User, UserProfile, Device
import datetime
from django.contrib.messages.api import get_messages
from social_auth import __version__ as version
import json
import settings as account_settings

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
    if not device_token or not device_token_type:
        return HttpResponse('bad data')
    
    if device_token_type != account_settings.IOS_TOKEN_TYPE_SANDBOX and device_token_type != account_settings.IOS_TOKEN_TYPE_DEVELOPMENT:
        return HttpResponse('bad data')
    
    device, created = Device.objects.get_or_create(user=request.user, ios_token=device_token, ios_token_type=device_token_type)
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
    