from celery.result import AsyncResult
from check_request import check_api_key_Authentication, check_http_method
from decorators import unlock_radio_on_exception
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import AnonymousUser, User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import Http404, HttpResponse, HttpResponseNotFound, \
    HttpResponseNotAllowed, HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from forms import SelectionForm
from models import Radio, RadioUser, SongInstance, SongUser, WallEvent, Playlist, \
    SongMetadata
from task import process_playlists, process_upload_song
from yaref.models import YasoundSong
import datetime
import import_utils
import json
import logging
import os
import settings as yabase_settings
import time
import uuid
import yabase.settings as yabase_settings
from django.utils.translation import ugettext_lazy as _


logger = logging.getLogger("yaapp.yabase")


PICTURE_FILE_TAG = 'picture'
SONG_FILE_TAG = 'song'

def task_status(request, task_id):
    asyncRes = AsyncResult(task_id=task_id)
    status = asyncRes.state
    progress = 0.5
    message = 'updating...'
    response_dict = {}
    response_dict['status'] = status
    response_dict['progress'] = progress
    if message:
   	 response_dict['message'] = message
    response = json.dumps(response_dict)
    return HttpResponse(response)


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
    filename = radio.build_picture_filename()

    # todo: delete old file
#    import pdb
#    pdb.set_trace()
#    if radio.picture and len(radio.picture.name) > 0:
#        print 'radio picture delete'
#        radio.picture.delete(save=True)
#    print 'radio picture save'
    radio.picture.save(filename, f, save=True)
    
    # for now, set also the UserProfile picture
    userprofile = radio.creator.userprofile
    # todo: delete old file
    filename = userprofile.build_picture_filename()
    userprofile.picture.save(filename, f, save=True)

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
    old_mood = song_user.mood
    song_user.mood = yabase_settings.MOOD_LIKE
    song_user.save()
    
    # add like event in wall
    if old_mood != yabase_settings.MOOD_LIKE:
        WallEvent.objects.add_like_event(request.user.userprofile.current_radio, song, request.user)
    
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

    favorites_playlist_name = yabase_settings.YASOUND_FAVORITES_PLAYLIST_NAME
    favorites_playlist_source_name = yabase_settings.YASOUND_FAVORITES_PLAYLIST_SOURCE_BASENAME
    favorites_playlist_source_name += '_'
    favorites_playlist_source_name += request.user.id
    playlist, created = radio.playlists.get_or_create(name=favorites_playlist_name, source=favorites_playlist_source_name)
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
    
    song = get_object_or_404(YasoundSong, id=nextsong.metadata.yasound_song_id)
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
    
    if not request.user.is_anonymous():
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
    
    if not request.user.is_anonymous():
        client = request.user
    else:
        if request.GET.has_key(CLIENT_ADDRESS_PARAM_NAME):
            client = request.GET[CLIENT_ADDRESS_PARAM_NAME]
        else:
            client = 'anonymous'
        
    res = '%s stopped listening to "%s" (listening duration = %d)' % (client, radio, listening_duration)
    return HttpResponse(res)

def get_current_song(request, radio_id):
    if not request.user.is_authenticated:
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
def upload_song(request, song_id=None):
    """
    Upload a song to the system.
    
    This view can be called by the mobile client or with regular form.
    song_id can be specified to match an already existing SongInstance object
    
    A metadata json dict can be provided.    
    
    """
    logger.info("upload song called")
    convert = True
    allow_unknown_song = True
    if not request.user.is_authenticated():
        key = request.REQUEST.get('key')
        if key != yabase_settings.UPLOAD_KEY:
            if not check_api_key_Authentication(request):
                return HttpResponse(status=401)
        else:
            convert = False # no conversion needed if request is coming from uploader
    if not check_http_method(request, ['post']):
        return HttpResponse(status=405)

    if not request.FILES.has_key(SONG_FILE_TAG):
        logger.info('upload_song: request does not contain song')
        logger.info(request.FILES)
        return HttpResponse('request does not contain a song file')

        
    json_data = {}
    data = request.REQUEST.get('data')
    if data:
        json_data = json.loads(data)
    else:
        logger.info('no metadata sent with binary')

    f = request.FILES[SONG_FILE_TAG]
    filename = f.name
    if filename == yabase_settings.DEFAULT_FILENAME:
        filename = import_utils.generate_default_filename(json_data) 
    
    json_data['filename'] = filename
    
    logger.info('importing song')
    process_upload_song(binary=f, metadata=json_data, convert=convert, song_id=song_id, allow_unknown_song=allow_unknown_song)

    res = 'upload OK for song: %s' % unicode(f.name)
    return HttpResponse(res)

@login_required
def upload_song_ajax(request):
    if not request.user.is_superuser:
        raise Http404
    radio_id = request.REQUEST.get('radio_id')
    radio_name = request.REQUEST.get('radio_name')
    creator_profile_id = request.REQUEST.get('creator_profile_id')
    
    metadata = {
        'radio_id': radio_id
    }
    global_message = u''
    if radio_name and radio_id:
        radio = Radio.objects.get(id=radio_id)
        radio.name = radio_name
        if creator_profile_id:
            user = User.objects.get(userprofile__id=creator_profile_id)
            radio.creator = user
            global_message = global_message + _('radio "%s" assigned to "%s"\n') % (radio, user)  
        radio.save()
             
    
    if 'file' in request.FILES:    
        f = request.FILES['file']
        sm, messages = import_utils.import_song(binary=f, metadata=metadata, convert=True, allow_unknown_song=True)
        json_data = json.JSONEncoder(ensure_ascii=False).encode({
            'success': True,
            'message': unicode(messages)
        })
        return HttpResponse(json_data, mimetype='text/html')
    else:
        for f in request.FILES.getlist('songs'):
            sm, messages = import_utils.import_song(binary=f, metadata=metadata, convert=True, allow_unknown_song=True)
            global_message = global_message + messages + '\n'
        json_data = json.JSONEncoder(ensure_ascii=False).encode({
            'success': True,
            'message': unicode(global_message)
        })
        return HttpResponse(json_data, mimetype='text/html')
        

@csrf_exempt
def add_song(request, radio_id, playlist_index, yasound_song_id):
    if not check_api_key_Authentication(request):
        return HttpResponse(status=401)
    if not check_http_method(request, ['post']):
        return HttpResponse(status=405)
    
    radio_id = int(radio_id)
    playlist_index = int(playlist_index)
    yasound_song_id = int(yasound_song_id)
    radio = get_object_or_404(Radio, id=radio_id)
    
    playlists = Playlist.objects.filter(radio=radio)
    if playlist_index > playlists.count():
        return HttpResponse(status=404)
    playlist = playlists[playlist_index]
    
    matched_songs = SongInstance.objects.filter(playlist__radio=radio, metadata__yasound_song_id=yasound_song_id)
    if matched_songs.count() > 0:
        res = dict(success=True, created=False, song_instance_id=matched_songs[0].id)
        response = json.dumps(res)
        return HttpResponse(response)
    
    yasound_song = get_object_or_404(YasoundSong, id=yasound_song_id)
    metadata, created = SongMetadata.objects.get_or_create(yasound_song_id=yasound_song_id, name=yasound_song.name, artist_name=yasound_song.artist_name, album_name=yasound_song.album_name)
    song_instance = SongInstance.objects.create(playlist=playlist, metadata=metadata)
    res = dict(success=True, created=True, song_instance_id=song_instance.id)
    response = json.dumps(res)
    return HttpResponse(response)

def song_instance_cover(request, song_instance_id):
    if not check_api_key_Authentication(request):
        return HttpResponse(status=401)
    if not check_http_method(request, ['get']):
        return HttpResponse(status=405)
    
    song_instance = get_object_or_404(SongInstance, id=song_instance_id)
    yasound_song = get_object_or_404(YasoundSong, id=song_instance.metadata.yasound_song_id)
    album = yasound_song.album
    if not album:
        return HttpResponseNotFound()
#    album = get_object_or_404(YasoundAlbum, id=album_id)
    url = album.cover_url
    if not url:
        url = '/media/images/default_image.png'
    return HttpResponseRedirect(url)
    

@login_required
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
def web_myradio(request, radio_uuid=None, template_name='web/my_radio.html'):
    radio = None
    if not uuid:
        radios = Radio.objects.filter(creator=request.user, ready=True)[0:1]
        if radios.count() == 0:
            raise Http404
        else:
            radio = radios[0]
    else:
        radio = get_object_or_404(Radio, uuid=radio_uuid)
    
    if not radio.ready:
        raise Http404
    
    radio_url = '%s%s' % (settings.YASOUND_STREAM_SERVER_URL, radio.uuid)
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
    
    
def web_index(request, template_name='web/index.html'):
    return render_to_response(template_name, {
    }, context_instance=RequestContext(request))  

    
def radio_unmatched_song(request, radio_id):
    radio = get_object_or_404(Radio, id=radio_id)
    unmatched_list = radio.unmatched_songs
    paginator = Paginator(unmatched_list, 25) # Show 25 songs per page
    page = request.GET.get('page', 1)
    try:
        unmatched = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        unmatched = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        unmatched = paginator.page(paginator.num_pages)

    print 'radio_unmatched_song view: %d songs' % unmatched.object_list.count()
    return render_to_response('yabase/unmatched.html', {"unmatched_songs": unmatched, "radio": radio})  
    
    
def status(request):
    User.objects.get(id=1)
    YasoundSong.objects.get(id=1)
    return HttpResponse('OK')
