from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from yabase.models import Radio, RadioUser
from celery.result import AsyncResult
import datetime
from tastypie.models import ApiKey
from django.contrib.auth.models import User
from yabase.task import process_playlists
import yabase.settings as yabase_settings

PICTURE_FILE_TAG = 'picture'

def authenticate_api_key(request):
    if not ('username' in request.GET and 'api_key' in request.GET):
        return False
    username = request.GET['username']
    key = request.GET['api_key']
    try:
        user = User.objects.get(username=username)
        api_key = ApiKey.objects.get(user=user)
        if api_key.key == key:
            request.user =user
        else:
            return False
    except User.DoesNotExist, ApiKey.DoesNotExist:
        return False
    return True

def task_status(request, task_id):
    asyncRes = AsyncResult(task_id=task_id)
    status = asyncRes.state
    return HttpResponse(status)


@csrf_exempt
def upload_playlists(request, radio_id):
    radio = get_object_or_404(Radio, pk=radio_id)

    print 'upload_playlists'
    print radio
    print request.FILES
    data = request.FILES['playlists_data']
    content_compressed = data.read()
    asyncRes = process_playlists.delay(radio, content_compressed)

    return HttpResponse(asyncRes.task_id)

@csrf_exempt
def set_radio_picture(request, radio_id):
    print 'set_radio_picture'
    try:
        radio = Radio.objects.get(id=radio_id)
    except Radio.DoesNotExist:
        return HttpResponse('radio does not exist')

    if not request.FILES.has_key(PICTURE_FILE_TAG):
        return HttpResponse('request does not contain a picture file')

    f = request.FILES[PICTURE_FILE_TAG]
    d = datetime.datetime.now()
    filename = unicode(d) + '.png'

    radio.picture.save(filename, f, save=True)

    res = 'picture OK for radio: %s' % unicode(radio)
    return HttpResponse(res)

@csrf_exempt
def like_radio(request, radio_id):
    if not authenticate_api_key(request):
        return HttpResponse(status=401)
    
    try:
        radio = Radio.objects.get(id=radio_id)
    except Radio.DoesNotExist:
        return HttpResponseNotFound()
    
    radio_user, created = RadioUser.objects.get_or_create(radio=radio, user=request.user)
    radio_user.mood = yabase_settings.MOOD_LIKE
    radio_user.save()
    res = '%s (user) likes %s (radio)\n' % (request.user, radio)
    return HttpResponse(res)

@csrf_exempt
def neutral_radio(request, radio_id):
    if not authenticate_api_key(request):
        return HttpResponse(status=401)
    
    try:
        radio = Radio.objects.get(id=radio_id)
    except Radio.DoesNotExist:
        return HttpResponseNotFound()
    
    radio_user, created = RadioUser.objects.get_or_create(radio=radio, user=request.user)
    radio_user.mood = yabase_settings.MOOD_NEUTRAL
    radio_user.save()
    res = '%s (user) does not like nor dislike %s (radio)\n' % (request.user, radio)
    return HttpResponse(res)

@csrf_exempt
def dislike_radio(request, radio_id):
    if not authenticate_api_key(request):
        return HttpResponse(status=401)
    
    try:
        radio = Radio.objects.get(id=radio_id)
    except Radio.DoesNotExist:
        return HttpResponseNotFound()
    
    radio_user, created = RadioUser.objects.get_or_create(radio=radio, user=request.user)
    radio_user.mood = yabase_settings.MOOD_DISLIKE
    radio_user.save()
    res = '%s (user) dislikes %s (radio)\n' % (request.user, radio)
    return HttpResponse(res)

@csrf_exempt
def favorite_radio(request, radio_id):
    if not authenticate_api_key(request):
        return HttpResponse(status=401)
    
    try:
        radio = Radio.objects.get(id=radio_id)
    except Radio.DoesNotExist:
        return HttpResponseNotFound()
    
    radio_user, created = RadioUser.objects.get_or_create(radio=radio, user=request.user)
    radio_user.favorite = True
    radio_user.save()
    res = '%s (user) has %s (radio) as favorite\n' % (request.user, radio)
    return HttpResponse(res)

@csrf_exempt
def not_favorite_radio(request, radio_id):
    if not authenticate_api_key(request):
        return HttpResponse(status=401)
    
    try:
        radio = Radio.objects.get(id=radio_id)
    except Radio.DoesNotExist:
        return HttpResponseNotFound()
    
    radio_user, created = RadioUser.objects.get_or_create(radio=radio, user=request.user)
    radio_user.favorite = False
    radio_user.save()
    res = '%s (user) has not %s (radio) as favorite anymore\n' % (request.user, radio)
    return HttpResponse(res)

    