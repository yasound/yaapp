from django.views.decorators.http import require_http_methods
from celery.result import AsyncResult
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse, HttpResponseNotFound, \
    HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from forms import SelectionForm
from models import Radio, RadioUser, SongInstance, SongUser, WallEvent, Playlist, \
    SongMetadata
from shutil import rmtree
from task import process_playlists, process_upload_song
from tempfile import mkdtemp
from yabase import signals as yabase_signals
from yaref.models import YasoundSong
import import_utils
import json
import logging
import os
import settings as yabase_settings
import uuid
from yacore.decorators import check_api_key
from yacore.http import check_api_key_Authentication, check_http_method
from tastypie.http import HttpNotFound

GET_NEXT_SONG_LOCK_EXPIRE = 60 * 3 # Lock expires in 3 minutes

logger = logging.getLogger("yaapp.yabase")


PICTURE_FILE_TAG = 'picture'
SONG_FILE_TAG = 'song'

def task_status(request, task_id):
    asyncRes = AsyncResult(task_id=task_id)
    status = asyncRes.state
    metadata = asyncRes.info
    if metadata is not None and 'progress' in metadata:
        progress = metadata['progress']
    else:
        progress = 0.0
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
    logger.debug('set_radio_picture')
    if not check_api_key_Authentication(request):
        logger.debug('set_radio_picture: athentication error')
        return HttpResponse(status=401)
    if not check_http_method(request, ['post']):
        logger.debug('set_radio_picture: http method error')
        return HttpResponse(status=405)

    try:
        radio = Radio.objects.get(id=radio_id)
    except Radio.DoesNotExist:
        logger.debug('set_radio_picture: radio does not exist')
        return HttpResponse('radio does not exist')

    if not request.FILES.has_key(PICTURE_FILE_TAG):
        logger.debug('set_radio_picture: request does not contain picture file')
        return HttpResponse('request does not contain a picture file')

    f = request.FILES[PICTURE_FILE_TAG]
#    filename = radio.build_picture_filename()
    
    radio.set_picture(f)
    
    # for now, set also the UserProfile picture
    userprofile = radio.creator.userprofile
    userprofile.set_picture(f)

    # todo: delete old file
#    import pdb
#    pdb.set_trace()
#    if radio.picture and len(radio.picture.name) > 0:
#        logger.debug('radio picture delete')
#        radio.picture.delete(save=True)
#    logger.debug('radio picture save')
#    radio.picture.save(filename, f, save=True)
#    logger.debug('radio picture saved')
#    
#    # for now, set also the UserProfile picture
#    logger.debug('save userprofile picture')
#    userprofile = radio.creator.userprofile
#    # todo: delete old file
#    filename = userprofile.build_picture_filename()
#    userprofile.picture.save(filename, f, save=True)
#    logger.debug('userprofile picture saved')

    res = 'picture OK for radio: %s' % unicode(radio)
    logger.debug(res)
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
    
    yabase_signals.like_radio.send(sender=radio, radio=radio, user=request.user)

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
    
    yabase_signals.neutral_like_radio.send(sender=radio, radio=radio, user=request.user)

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
    
    yabase_signals.dislike_radio.send(sender=radio, radio=radio, user=request.user)
    
    res = '%s (user) dislikes %s (radio)\n' % (request.user, radio)
    return HttpResponse(res)

@csrf_exempt
@check_api_key(methods=['POST'], login_required=True)
def favorite_radio(request, radio_id):
    try:
        radio = Radio.objects.get(id=radio_id)
    except Radio.DoesNotExist:
        return HttpResponseNotFound()

    radio_user, _created = RadioUser.objects.get_or_create(radio=radio, user=request.user)
    radio_user.favorite = True
    radio_user.save()
    
    yabase_signals.favorite_radio.send(sender=radio, radio=radio, user=request.user)
    
    res = '%s (user) has %s (radio) as favorite\n' % (request.user, radio)
    return HttpResponse(res)

@csrf_exempt
@check_api_key(methods=['POST'], login_required=True)
def not_favorite_radio(request, radio_id):
    try:
        radio = Radio.objects.get(id=radio_id)
    except Radio.DoesNotExist:
        return HttpResponseNotFound()

    radio_user, _created = RadioUser.objects.get_or_create(radio=radio, user=request.user)
    radio_user.favorite = False
    radio_user.save()
    
    yabase_signals.not_favorite_radio.send(sender=radio, radio=radio, user=request.user)

    res = '%s (user) has not %s (radio) as favorite anymore\n' % (request.user, radio)
    return HttpResponse(res)

@csrf_exempt
def radio_shared(request, radio_id):
    if not check_api_key_Authentication(request):
        return HttpResponse(status=401)

    if not check_http_method(request, ['post']):
        return HttpResponse(status=405)

    try:
        radio = Radio.objects.get(id=radio_id)
    except Radio.DoesNotExist:
        return HttpResponseNotFound()

    radio.shared(request.user)
    res = 'user %s has shared radio %s' % (request.user.userprofile.name, radio.name)
    return HttpResponse(res)



# SONG USER
@csrf_exempt
@check_api_key(methods=['POST',])
def like_song(request, song_id):
    try:
        song = SongInstance.objects.get(id=song_id)
    except SongInstance.DoesNotExist:
        song = None

    radio = song.playlist.radio
    if radio and not radio.is_live():
        song_user, _created = SongUser.objects.get_or_create(song=song, user=request.user)
        song_user.mood = yabase_settings.MOOD_LIKE
        song_user.save()
    
    # add like event in wall
    if radio is not None:
        WallEvent.objects.add_like_event(radio, song, request.user)
    
    res = '%s (user) likes %s (song)\n' % (request.user, song)
    return HttpResponse(res)

@csrf_exempt
@check_api_key(methods=['POST',])
def post_message(request, radio_id):
    message = request.REQUEST.get('message')
    radio = get_object_or_404(Radio, uuid=radio_id)
    radio.post_message(request.user, message)
    return HttpResponse(status=200)

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


@csrf_exempt
def get_next_song(request, radio_id):
    radio = get_object_or_404(Radio, uuid=radio_id)

    lock_id = "get_next_song_%d" % (radio.id)
    acquire_lock = lambda: cache.add(lock_id, "true", GET_NEXT_SONG_LOCK_EXPIRE)
    release_lock = lambda: cache.delete(lock_id)

    if not acquire_lock():
        logger.info('get_next_song locked for radio %d' % (radio.id))
        return HttpResponse('computing next songs already set', status=404)

    try:
        nextsong = radio.get_next_song()
    finally:
        release_lock()
        
    if not nextsong:
        return HttpResponse('cannot find next song', status=404)
    
    song = get_object_or_404(YasoundSong, id=nextsong.metadata.yasound_song_id)
    return HttpResponse(song.filename)

@csrf_exempt
def connect_to_radio(request, radio_id):
    if not request.user.is_authenticated():
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
    if not request.user.is_authenticated():
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
    
    logger.debug('stop_listening_to_radio (uid=%s): %s', radio_uuid, request.REQUEST)
    
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
    check_api_key_Authentication(request)

    if not check_http_method(request, ['get']):
        return HttpResponse(status=405)
    
    song_json = SongInstance.objects.get_current_song_json(radio_id)
    if song_json is None:
        return HttpResponseNotFound()
    
    return HttpResponse(song_json)


@check_api_key(methods=['GET',], login_required=False)
def buy_link(request, radio_id):
    radio = get_object_or_404(Radio, id=radio_id)
    song_instance = radio.current_song
    if not song_instance:
        return HttpResponseRedirect(reverse('buy_link_not_found'))

    song_metadata = song_instance.metadata
    yasound_song_id = song_metadata.yasound_song_id
    if not yasound_song_id:
        return HttpResponseRedirect(reverse('buy_link_not_found'))
    
    try:
        yasound_song = YasoundSong.objects.get(id=yasound_song_id)
    except YasoundSong.DoesNotExist:
        return HttpResponseRedirect(reverse('buy_link_not_found'))
        
    url = yasound_song.generate_buy_link()
    if not url:
        return HttpResponseRedirect(reverse('buy_link_not_found'))
    else:
        return HttpResponseRedirect(url)

def buy_link_not_found(request, template_name='yabase/buy_link_not_found.html'):
    return render_to_response(template_name, {
    }, context_instance=RequestContext(request))    


@csrf_exempt
def upload_song(request, song_id=None):
    """
    Upload a song to the system.
    
    This view can be called by the mobile client or with regular form.
    song_id can be specified to match an already existing SongInstance object
    
    A metadata json dict can be provided.    
    
    """
    logger.info("upload song called")
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
    
    directory = mkdtemp(dir=settings.TEMP_DIRECTORY)
    _path, extension = os.path.splitext(f.name)
    source = u'%s/s%s' % (directory, extension)
    source_f = open(source , 'wb')
    for chunk in f.chunks():
        source_f.write(chunk)
    source_f.close()
    
    logger.info('importing song')
    process_upload_song.delay(filepath=source, 
                              metadata=json_data, 
                              convert=True, 
                              song_id=song_id, 
                              allow_unknown_song=True)

    res = 'upload OK for song: %s' % unicode(f.name)
    return HttpResponse(res)

@login_required
def upload_song_ajax(request):
    if not request.user.is_superuser:
        raise Http404
    radio_id = request.REQUEST.get('radio_id')
    radio_name = request.REQUEST.get('radio_name')
    song_metadata_id = request.REQUEST.get('song_metadata_id')
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
        directory = mkdtemp(dir=settings.TEMP_DIRECTORY)
        _path, extension = os.path.splitext(f.name)
        source = u'%s/s%s' % (directory, extension)
        source_f = open(source , 'wb')
        for chunk in f.chunks():
            source_f.write(chunk)
        source_f.close()

        _sm, messages = import_utils.import_song(filepath=source, 
                                                 metadata=metadata, 
                                                 convert=True, 
                                                 allow_unknown_song=True,
                                                 song_metadata_id=song_metadata_id)
        rmtree(directory)
        json_data = json.JSONEncoder(ensure_ascii=False).encode({
            'success': True,
            'message': unicode(messages)
        })
        return HttpResponse(json_data, mimetype='text/html')
    else:
        for f in request.FILES.getlist('songs'):
            directory = mkdtemp(dir=settings.TEMP_DIRECTORY)
            _path, extension = os.path.splitext(f.name)
            source = u'%s/s%s' % (directory, extension)
            source_f = open(source , 'wb')
            for chunk in f.chunks():
                source_f.write(chunk)
            source_f.close()
            
            sm, messages = import_utils.import_song(filepath=source, 
                                                    metadata=metadata, 
                                                    convert=True, 
                                                    allow_unknown_song=True,
                                                    song_metadata_id=song_metadata_id)
            rmtree(directory)
            
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
    
    # yasound_song fields can be null, we replace them if empty values
    name=yasound_song.name
    artist_name=yasound_song.artist_name
    if not artist_name:
        artist_name = ''
    
    album_name=yasound_song.album_name
    if not album_name:
        album_name = ''
    
    metadata, _created = SongMetadata.objects.get_or_create(yasound_song_id=yasound_song_id, name=name, artist_name=artist_name, album_name=album_name)
    song_instance = SongInstance.objects.create(playlist=playlist, metadata=metadata)
    res = dict(success=True, created=True, song_instance_id=song_instance.id)
    response = json.dumps(res)
    return HttpResponse(response)


@check_api_key(methods=['GET'], login_required=True)
def reject_song(request, song_instance):
    if request.user != song_instance.playlist.radio.creator:
        return HttpNotFound()
    
    radio = song_instance.playlist.radio
    radio.reject_song(song_instance)
    

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
    

def web_listen(request, radio_uuid, template_name='yabase/listen.html'):
    radio = None
    try:
        radio = Radio.objects.get(uuid=radio_uuid)
    except Radio.DoesNotExist:
        if len(radio_uuid) > 4:
            radios = Radio.objects.filter(uuid__startswith=radio_uuid)[:1]
            if radios.count() > 0:
                radio = radios[0]
                url = reverse('yabase.views.web_listen', args=[radio.uuid])
                return HttpResponseRedirect(url)

    if radio is None:
        raise Http404

    radio_url = '%s%s' % (settings.YASOUND_STREAM_SERVER_URL, radio_uuid)
    return render_to_response(template_name, {
        "radio": radio,
        "radio_url": radio_url,
        "listeners": radio.radiouser_set.filter(listening=True).count(),
        "fans": radio.radiouser_set.filter(favorite=True).count(),
        "new_page": '/app/#radio/%s' % (radio_uuid)
    }, context_instance=RequestContext(request))    

def web_app(request, radio_uuid=None, query=None, user_id=None, template_name='yabase/webapp.html'):
    if not request.user.is_superuser:
        raise Http404()
    
    if request.user.is_authenticated():
        user_uuid = request.user.get_profile().own_radio.uuid
    else:
        user_uuid = 0
        
    push_url = settings.YASOUND_PUSH_URL
    enable_push = settings.ENABLE_PUSH
    
    facebook_share_picture = request.build_absolute_uri(settings.FACEBOOK_SHARE_PICTURE)
    facebook_share_link = request.build_absolute_uri(reverse('webapp'))
    
    return render_to_response(template_name, {
        'user_uuid': user_uuid,
        'user_id' : user_id,
        'push_url': push_url,
        'enable_push': enable_push,
        'current_uuid': radio_uuid,
        'facebook_app_id': settings.FACEBOOK_APP_ID,
        'facebook_share_picture': facebook_share_picture,
        'facebook_share_link': facebook_share_link
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
    return HttpResponseRedirect(settings.PUBLIC_WEBSITE_URL)
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
    User.objects.all()[:1]
    YasoundSong.objects.all()[:1]
    return HttpResponse('OK')


@check_api_key(methods=['PUT', 'DELETE'])
def delete_song_instance(request, song_instance_id):
    song = get_object_or_404(SongInstance, pk=song_instance_id)
    
    if request.user != song.playlist.radio.creator:
        return HttpResponse(status=401)
    
    song.delete()
    
    # if radio has no more songs, set ready to False
    radio = song.playlist.radio
    song_count = SongInstance.objects.filter(playlist__radio=radio, metadata__yasound_song_id__gt=0).count()
    if song_count == 0:
        radio.ready = False
        radio.save()
    
    response = {'success':True}
    res = json.dumps(response)
    return HttpResponse(res)

@csrf_exempt
def notify_missing_song(request):
    local_logger = logging.getLogger("yaapp.missing_songs")
    name = request.REQUEST.get('name')
    local_logger.info('missing: %s' % name)
    
    return HttpResponse('OK')
    
    
@csrf_exempt
def radio_live(request, radio_uuid):
    radio = get_object_or_404(Radio, uuid=radio_uuid)
    action = request.REQUEST.get('action')
    if action and action == 'stop':
        radio.set_live(enabled=False)
    else :
        name = request.REQUEST.get('name')
        artist = request.REQUEST.get('artist')
        album = request.REQUEST.get('album')
        
        id = None
        if radio.current_song:
            id = radio.current_song.id
        
        radio.set_live(enabled=True, name=name, album=album, artist=artist, id=id)
    return HttpResponse('OK')
    
    
    