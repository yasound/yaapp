from django.http import HttpResponse, HttpResponseNotFound, HttpResponseNotAllowed, HttpResponseBadRequest
from django.shortcuts import render_to_response, get_object_or_404
from django.http import Http404
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from models import Radio, RadioUser, SongInstance, SongUser, YasoundSong, WallEvent
from celery.result import AsyncResult
import datetime
import json
from task import process_playlists
import settings as yabase_settings
from django.conf import settings
from check_request import check_api_key_Authentication, check_http_method
import time
from django.contrib.auth.models import AnonymousUser

PICTURE_FILE_TAG = 'picture'

def task_status(request, task_id):
    asyncRes = AsyncResult(task_id=task_id)
    status = asyncRes.state
    return HttpResponse(status)


@csrf_exempt
def upload_playlists(request, radio_id):
    if not check_api_key_Authentication(request):
        return HttpResponse(status=401)
    if not check_http_method(request, ['post']):
        return HttpResponse(status=405)

    radio = get_object_or_404(Radio, pk=radio_id)
    data = request.FILES['playlists_data']
    content_compressed = data.read()
    asyncRes = process_playlists.delay(radio, content_compressed)

    return HttpResponse(asyncRes.task_id)

@csrf_exempt
def set_radio_picture(request, radio_id):
    if not check_api_key_Authentication(request):
        return HttpResponse(status=401)
    if not check_http_method(request, ['post']):
        return HttpResponse(status=405)

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
    if not check_api_key_Authentication(request):
        return HttpResponse(status=401)

    if not check_http_method(request, ['post']):
        return HttpResponse(status=405)

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
    if not check_api_key_Authentication(request):
        return HttpResponse(status=401)

    if not check_http_method(request, ['post']):
        return HttpResponse(status=405)

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
    if not check_api_key_Authentication(request):
        return HttpResponse(status=401)

    if not check_http_method(request, ['post']):
        return HttpResponse(status=405)

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
    if not check_api_key_Authentication(request):
        return HttpResponse(status=401)

    if not check_http_method(request, ['post']):
        return HttpResponse(status=405)

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
    if not check_api_key_Authentication(request):
        return HttpResponse(status=401)

    if not check_http_method(request, ['post']):
        return HttpResponse(status=405)

    try:
        radio = Radio.objects.get(id=radio_id)
    except Radio.DoesNotExist:
        return HttpResponseNotFound()

    radio_user, created = RadioUser.objects.get_or_create(radio=radio, user=request.user)
    radio_user.favorite = False
    radio_user.save()
    res = '%s (user) has not %s (radio) as favorite anymore\n' % (request.user, radio)
    return HttpResponse(res)



# SONG USER
@csrf_exempt
def like_song(request, song_id):
    if not check_api_key_Authentication(request):
        return HttpResponse(status=401)

    if not check_http_method(request, ['post']):
        return HttpResponse(status=405)

    try:
        song = SongInstance.objects.get(id=song_id)
    except SongInstance.DoesNotExist:
        return HttpResponseNotFound()

    song_user, created = SongUser.objects.get_or_create(song=song, user=request.user)
    song_user.mood = yabase_settings.MOOD_LIKE
    song_user.save()
    res = '%s (user) likes %s (song)\n' % (request.user, song)
    return HttpResponse(res)

@csrf_exempt
def neutral_song(request, song_id):
    if not check_api_key_Authentication(request):
        return HttpResponse(status=401)

    if not check_http_method(request, ['post']):
        return HttpResponse(status=405)

    try:
        song = SongInstance.objects.get(id=song_id)
    except SongInstance.DoesNotExist:
        return HttpResponseNotFound()

    song_user, created = SongUser.objects.get_or_create(song=song, user=request.user)
    song_user.mood = yabase_settings.MOOD_NEUTRAL
    song_user.save()
    res = '%s (user) does not like nor dislike %s (song)\n' % (request.user, song)
    return HttpResponse(res)

@csrf_exempt
def dislike_song(request, song_id):
    if not check_api_key_Authentication(request):
        return HttpResponse(status=401)

    if not check_http_method(request, ['post']):
        return HttpResponse(status=405)

    try:
        song = SongInstance.objects.get(id=song_id)
    except SongInstance.DoesNotExist:
        return HttpResponseNotFound()

    song_user, created = SongUser.objects.get_or_create(song=song, user=request.user)
    song_user.mood = yabase_settings.MOOD_DISLIKE
    song_user.save()
    res = '%s (user) dislikes %s (song)\n' % (request.user, song)
    return HttpResponse(res)



@csrf_exempt
def add_song_to_favorites(request, radio_id):
    if not check_api_key_Authentication(request):
        return HttpResponse(status=401)

    if not check_http_method(request, ['post']):
        return HttpResponse(status=405)

    try:
        radio = Radio.objects.get(id=radio_id)
        if not request.user or request.user != radio.creator:
            return HttpResponse(status=401)
    except Radio.DoesNotExist:
        return HttpResponseNotFound()

    if len(request.POST.keys()) == 0:
        return HttpResponseBadRequest()
    data = request.POST.keys()[0]
    obj = json.loads(data)
    if not 'id' in obj:
        return HttpResponseBadRequest()

    try:
        song_id = int(obj['id'])
        song_source = SongInstance.objects.get(id=song_id)
    except SongInstance.DoesNotExist:
        return HttpResponseBadRequest()

    already_in_radio = SongInstance.objects.filter(playlist__in=radio.playlists.all(), song=song_source.song).count() > 0
    if already_in_radio:
        result = dict(success=True, created=False)
        response = json.dumps(result)
        return HttpResponse(response)

    YASOUND_FAVORITES_PLAYLIST_NAME = '#yasound_songs_from_other_radios'
    YASOUND_FAVORITES_PLAYLIST_SOURCE = '#yasound_songs_from_other_radios_source_%d' % request.user.id
    playlist, created = radio.playlists.get_or_create(name=YASOUND_FAVORITES_PLAYLIST_NAME, source=YASOUND_FAVORITES_PLAYLIST_SOURCE)
    new_song = SongInstance.objects.create(playlist=playlist, metadata=song_source.metadata, song=song_source.song, play_count=0)

    result = dict(success=True, created=True)
    response = json.dumps(result)
    return HttpResponse(response)

@csrf_exempt
def get_next_song(request, radio_id):
    radio = get_object_or_404(Radio, uuid=radio_id)
    
    i = 0
    while radio.is_locked:
        time.sleep(3)
        i = i+1
        if i > 2:
            break
    
    if radio.is_locked:
        return HttpResponse('computing next songs already set', status=404)
    
    radio.lock()
    nextsong = radio.get_next_song()
    radio.unlock()
    
    if not nextsong:
        return HttpResponse('cannot find next song', status=404)
    
    song = get_object_or_404(YasoundSong, id=nextsong.song)
    return HttpResponse(song.filename)

@csrf_exempt
def start_listening_to_radio(request, radio_uuid):
    check_api_key_Authentication(request) # set request.user

    if not check_http_method(request, ['post']):
        return HttpResponse(status=405)
    
    radio = get_object_or_404(Radio, uuid=radio_uuid)
    
    if not request.user.is_anonymous():
        event = WallEvent.objects.create(user=request.user, radio=radio, type=yabase_settings.EVENT_STARTED_LISTEN)
        res = '%s stopped listening to %s' % (event.user.userprofile.name, event.radio.name)
    else:
        if not request.GET.has_key('address'):
            return HttpResponseBadRequest()
        address = request.GET['address']
        event = WallEvent.objects.create(radio=radio, type=yabase_settings.EVENT_STARTED_LISTEN, text=address)
        res = '%s stopped listening to %s' % (event.text, event.radio.name)

    return HttpResponse(res)

@csrf_exempt
def stop_listening_to_radio(request, radio_uuid):
    check_api_key_Authentication(request) # set request.user

    if not check_http_method(request, ['post']):
        return HttpResponse(status=405)
    
    radio = get_object_or_404(Radio, uuid=radio_uuid)
    
    if not request.user.is_anonymous():
        event = WallEvent.objects.create(user=request.user, radio=radio, type=yabase_settings.EVENT_STOPPED_LISTEN)
        res = '%s stopped listening to %s' % (event.user.userprofile.name, event.radio.name)
    else:
        if not request.GET.has_key('address'):
            return HttpResponseBadRequest()
        address = request.GET['address']
        event = WallEvent.objects.create(radio=radio, type=yabase_settings.EVENT_STOPPED_LISTEN, text=address)
        res = '%s stopped listening to %s' % (event.text, event.radio.name)

    return HttpResponse(res)


def web_listen(request, radio_uuid, template_name='yabase/listen.html'):
    radio = get_object_or_404(Radio, uuid=radio_uuid)
    radio_url = '%s%s' % (settings.YASOUND_STREAM_SERVER_URL, radio_uuid)
    return render_to_response(template_name, {
        "radio": radio,
        "radio_url": radio_url,
        "listeners": radio.radiouser_set.filter(listening=True).count(),
        "fans": radio.radiouser_set.filter(favorite=True).count()
    }, context_instance=RequestContext(request))    
    
    
