from celery.result import AsyncResult
from check_request import check_api_key_Authentication, check_http_method
from django.conf import settings
from django.http import Http404, HttpResponse, HttpResponseNotFound, \
    HttpResponseNotAllowed, HttpResponseBadRequest
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from models import Radio, RadioUser, SongInstance, SongUser, WallEvent
from task import process_playlists
from yaref.models import YasoundSong
import datetime
import json
import settings as yabase_settings
import time
from django.contrib.auth.models import AnonymousUser
from decorators import unlock_radio_on_exception
from django.contrib.auth.decorators import login_required
from forms import SelectionForm
import uuid

import logging
logger = logging.getLogger("yaapp.yabase")


PICTURE_FILE_TAG = 'picture'
SONG_FILE_TAG = 'song'

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
    print 'set_radio_picture'
    if not check_api_key_Authentication(request):
        print 'set_radio_picture: athentication error'
        return HttpResponse(status=401)
    if not check_http_method(request, ['post']):
        print 'set_radio_picture: http method error'
        return HttpResponse(status=405)

    try:
        radio = Radio.objects.get(id=radio_id)
    except Radio.DoesNotExist:
        print 'set_radio_picture: radio does not exist'
        return HttpResponse('radio does not exist')

    if not request.FILES.has_key(PICTURE_FILE_TAG):
        print 'set_radio_picture: request does not contain picture file'
        return HttpResponse('request does not contain a picture file')

    f = request.FILES[PICTURE_FILE_TAG]
    d = datetime.datetime.now()
    filename = unicode(d) + '.png'

    radio.picture.save(filename, f, save=True)
    
    # for now, set also the UserProfile picture
    userprofile = radio.creator.userprofile
    userprofile.picture = radio.picture
    userprofile.save()

    res = 'picture OK for radio: %s' % unicode(radio)
    print 'set_radio_picture: OK (%s)' % res
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


def get_song_status(request, song_id):
    if not check_api_key_Authentication(request):
        return HttpResponse(status=401)

    if not check_http_method(request, ['get']):
        return HttpResponse(status=405)
    
    song = get_object_or_404(SongInstance, id=song_id)
    status_dict = song.song_status
    res = json.dumps(status_dict)
    return HttpResponse(res)


@unlock_radio_on_exception
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
def connect_to_radio(request, radio_id):
    if not check_api_key_Authentication(request):
        return HttpResponse(status=401)

    if not check_http_method(request, ['post']):
        return HttpResponse(status=405)
    
    radio = get_object_or_404(Radio, id=radio_id)
    radio_user, created = RadioUser.objects.get_or_create(radio=radio, user=request.user)
    radio_user.connected = True
    radio_user.save()
    
    res = '%s connected to "%s"' % (request.user, radio)
    return HttpResponse(res)
    
@csrf_exempt
def disconnect_from_radio(request, radio_id):
    if not check_api_key_Authentication(request):
        return HttpResponse(status=401)

    if not check_http_method(request, ['post']):
        return HttpResponse(status=405)
    
    radio = get_object_or_404(Radio, id=radio_id)
    radio_user, created = RadioUser.objects.get_or_create(radio=radio, user=request.user)
    radio_user.connected = False
    radio_user.save()
    
    res = '%s disconnected from "%s"' % (request.user, radio)
    return HttpResponse(res)



CLIENT_ADDRESS_PARAM_NAME = 'address'

@csrf_exempt
def start_listening_to_radio(request, radio_uuid):
    check_api_key_Authentication(request)

    if not check_http_method(request, ['post']):
        return HttpResponse(status=405)
    
    radio = get_object_or_404(Radio, uuid=radio_uuid)
    radio.user_started_listening(request.user)
    
    if not request.user.is_anonymous:
        client = request.user
    else:
        if request.GET.has_key(CLIENT_ADDRESS_PARAM_NAME):
            client = request.GET[CLIENT_ADDRESS_PARAM_NAME]
        else:
            client = 'anonymous'
        
    res = '%s is listening to "%s"' % (client, radio)
    return HttpResponse(res)

@csrf_exempt
def stop_listening_to_radio(request, radio_uuid):
    check_api_key_Authentication(request)

    if not check_http_method(request, ['post']):
        return HttpResponse(status=405)
        
    LISTENING_DURATION_PARAM_NAME = 'listening_duration'
    listening_duration = int(request.GET.get(LISTENING_DURATION_PARAM_NAME, 0))
    
    radio = get_object_or_404(Radio, uuid=radio_uuid)
    radio.user_stopped_listening(request.user, listening_duration)
    
    if not request.user.is_anonymous:
        client = request.user
    else:
        if request.GET.has_key(CLIENT_ADDRESS_PARAM_NAME):
            client = request.GET[CLIENT_ADDRESS_PARAM_NAME]
        else:
            client = 'anonymous'
        
    res = '%s stopped listening to "%s" (listening duration = %d)' % (client, radio, listening_duration)
    return HttpResponse(res)

def get_current_song(request, radio_id):
    if not check_api_key_Authentication(request):
        return HttpResponse(status=401)

    if not check_http_method(request, ['get']):
        return HttpResponse(status=405)
    
    radio = get_object_or_404(Radio, id=radio_id)
    song_instance = radio.current_song
    if not song_instance:
        return HttpResponseNotFound()
    song_dict = song_instance.song_description
    if not song_dict:
        return HttpResponseNotFound()
    
    song_json = json.dumps(song_dict)
    return HttpResponse(song_json)

@csrf_exempt
def upload_song(request):
    if not check_api_key_Authentication(request):
        return HttpResponse(status=401)
    if not check_http_method(request, ['post']):
        return HttpResponse(status=405)

    if not request.FILES.has_key(SONG_FILE_TAG):
        logger.info('upload_song: request does not contain song')
        return HttpResponse('request does not contain a song file')

    f = request.FILES[SONG_FILE_TAG]
    filename = uuid.uuid1() + '.mp3'
    path = '%s%s' % (settings.UPLOAD_SONG_FOLDER, filename)
    destination = open(path, 'wb')
    for chunk in f.chunks():
        destination.write(chunk)
    destination.close()
    
    res = 'upload OK for song: %s' % unicode(f.name)
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
    
def radios(request, template_name='web/radios.html'):
    return render_to_response(template_name, {
    }, context_instance=RequestContext(request))    
        
@login_required
def web_myradio(request, template_name='web/my_radio.html'):
    radio = get_object_or_404(Radio, creator=request.user)
    radio_uuid = radio.uuid
    radio_url = '%s%s' % (settings.YASOUND_STREAM_SERVER_URL, radio_uuid)
    return render_to_response(template_name, {
        "radio": radio,
        "radio_url": radio_url,
        "listeners": radio.radiouser_set.filter(listening=True).count(),
        "fans": radio.radiouser_set.filter(favorite=True).count()
    }, context_instance=RequestContext(request))    

@login_required
def web_friends(request, template_name='web/friends.html'):
    friends = request.user.userprofile.friends.all()
    return render_to_response(template_name, {
        "friends": friends,
    }, context_instance=RequestContext(request))    
    
@login_required
def web_favorites(request, template_name='web/favorites.html'):
    radios = Radio.objects.filter(radiouser__user=request.user, radiouser__favorite=True)
    return render_to_response(template_name, {
        "radios": radios,
    }, context_instance=RequestContext(request))    


@login_required
def web_selections(request, template_name='web/selections.html', form_class=SelectionForm):
    form = form_class(request.REQUEST)
    radios = Radio.objects.filter(radiouser__user=request.user, radiouser__favorite=True)
    if form.is_valid():
        genre = form.cleaned_data['genre']
        if len(genre) > 0:
            radios = Radio.objects.filter(radiouser__user=request.user, radiouser__favorite=True, genre=genre)
    return render_to_response(template_name, {
        "radios": radios,
        "form": form,
    }, context_instance=RequestContext(request))    

@login_required
def web_favorite(request, radio_uuid, template_name='web/favorite.html'):
    radio = get_object_or_404(Radio, uuid=radio_uuid)
    radio_url = '%s%s' % (settings.YASOUND_STREAM_SERVER_URL, radio_uuid)
    return render_to_response(template_name, {
        "radio": radio,
        "radio_url": radio_url,
        "listeners": radio.radiouser_set.filter(listening=True).count(),
        "fans": radio.radiouser_set.filter(favorite=True).count()
    }, context_instance=RequestContext(request))    

def web_terms(request, template_name='web/terms.html'):
    return render_to_response(template_name, {
    }, context_instance=RequestContext(request))    
    
    