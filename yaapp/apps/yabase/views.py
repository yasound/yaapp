from account import settings as account_settings
from account.models import UserProfile
from celery.result import AsyncResult
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.contrib.humanize.templatetags.humanize import intcomma
from django.core.cache import cache
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse, HttpResponseNotFound, \
    HttpResponseBadRequest, HttpResponseRedirect, HttpResponsePermanentRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.views.generic.base import View
from forms import SettingsRadioForm, NewRadioForm
from models import Radio, RadioUser, SongInstance, SongUser, WallEvent, Playlist, \
    SongMetadata, Announcement
from shutil import rmtree
from stats.models import RadioListeningStat
from task import process_playlists, process_upload_song, async_song_played, async_songs_started
from tastypie.http import HttpNotFound
from tastypie.models import ApiKey
from tempfile import mkdtemp
from yabase import signals as yabase_signals
from yabase.forms import SettingsUserForm, SettingsFacebookForm, \
    SettingsTwitterForm, ImportItunesForm, RadioGenreForm
from forms import MyAccountsForm, MyInformationsForm, MyNotificationsForm
from account.forms import WebAppSignupForm, LoginForm
from yacore.api import api_response, MongoAwareEncoder
from yacore.binary import BinaryData
from yacore.decorators import check_api_key
from yacore.http import check_api_key_Authentication, check_http_method, absolute_url, is_iphone, is_deezer
from yacore.geoip import request_country, request_city_record
from yamessage.models import NotificationsManager
from yametrics.models import GlobalMetricsManager
from yarecommendation.models import ClassifiedRadiosManager, RadioRecommendationsCache
from yaref.models import YasoundSong
import yasearch.search as yasearch_search
from yasearch.models import RadiosManager
from yageoperm import utils as yageoperm_utils
from yahistory.models import ProgrammingHistory
from yawall.models import WallManager
from account.views import fast_connected_users_by_distance
import import_utils
import json
import logging
import os
import requests
import settings as yabase_settings
import uuid
import zlib
import urllib
import mimetypes


from account.models import InvitationsManager, AnonymousManager
from yapremium.task import async_check_for_invitation

from django.http import HttpResponseForbidden
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
        progress = '1.0'

    message = 'updating...'
    response_dict = {}
    response_dict['status'] = status
    response_dict['progress'] = progress
    if message:
        response_dict['message'] = message
    response = json.dumps(response_dict)
    return HttpResponse(response)


def get_root(request, app_name):
    if len(app_name) > 0:
        root = '/' + app_name + '/'
    else:
        root = '/'

    if app_name == 'app':
        root = '/'

    if app_name != 'deezer':
        root = '/' + request.LANGUAGE_CODE + root
    return root


def get_alternate_language_urls(request):
    from localeurl import utils as localeurl_utils

    path = request.path
    alternate_urls = []
    for code, name in settings.LANGUAGES:
        if request.LANGUAGE_CODE == code:
            continue
        locale, path = localeurl_utils.strip_path(path)

        localized_url = absolute_url(localeurl_utils.locale_url(path, code))
        alternate_urls.append((code, localized_url))

    return alternate_urls


@csrf_exempt
def upload_playlists(request, radio_id):
    if not check_api_key_Authentication(request):
        return HttpResponse(status=401)
    if not check_http_method(request, ['post']):
        return HttpResponse(status=405)

    radio = get_object_or_404(Radio, pk=radio_id)

    if radio.ready:
        yabase_signals.new_animator_activity.send(sender=request.user,
                                                  user=request.user,
                                                  radio=radio,
                                                  atype=yabase_settings.ANIMATOR_TYPE_UPLOAD_PLAYLIST)

    data = request.FILES['playlists_data']
    content_compressed = data.read()
    asyncRes = process_playlists.delay(radio, content_compressed)

    return HttpResponse(asyncRes.task_id)

def radio_recommendations_process(request, internal=False, genre=''):
    # read url params
    limit = int(request.GET.get('limit', yabase_settings.MOST_ACTIVE_RADIOS_LIMIT))
    skip = int(request.GET.get('skip', 0))
    if genre == '':
        genre = request.GET.get('genre', '')
    recommendation_token = request.GET.get('token', None)
    # check if artist list is provided
    artist_data_file = None
    if request.method == 'POST':
        artist_data_file = request.FILES.get('artists_data', None)
    artist_data = None
    if artist_data_file:
        artist_data_compressed = artist_data_file.read()
        if len(artist_data_compressed) > 0:
            try:
                artist_data = zlib.decompress(artist_data_compressed)
            except Exception, e:
                logger.error("Cannot handle content_compressed: %s" % (unicode(e)))

    recommendations = None
    if recommendation_token is not None:
        # read radio recommendations from mongodb. they have computed and stored in a previous call
        cache_manager = RadioRecommendationsCache()
        recommendations = cache_manager.get_recommendations(recommendation_token)

    if recommendations is None:
        # 1 - try to get artist list
        artists = None
        if artist_data is not None:
            # build artist list from binary data
            binary = BinaryData(artist_data)
            artists = []
            while not binary.is_done():
                tag = binary.get_tag()
                a = binary.get_string()
                _song_count = binary.get_int16()  # not used for now, but needs to be read to go forward in binary stream
                if tag == 'ARTS':
                    artists.append(a)
        elif request.user is not None and request.user.is_authenticated():
            # try to load artist list from mongo
            cache_manager = RadioRecommendationsCache()
            artists = cache_manager.get_artists(request.user)
        if artists is not None and len(artists) > 0:
            # 2 - compute recommendations from artist list
            m = ClassifiedRadiosManager()
            res = m.find_similar_radios(artists, offset=0, limit=yabase_settings.RADIO_RECOMMENDATION_COMPUTE_COUNT)
            radio_ids = [int(x[1]) for x in res]
            recommendations = radio_ids
            # 3 - cache recommendations
            cache_manager = RadioRecommendationsCache()
            recommendation_token = cache_manager.save_recommendations(recommendations)

    if recommendations is None:
        recommendations = []  # no recommendations

    # recommendation starts with editorial selection
    qs = Radio.objects.ready_objects()
    if genre != '':
        qs = qs.filter(genre=genre)

    if is_iphone(request) or is_deezer(request):
        selection_radios = qs.filter(featuredcontent__activated=True, featuredcontent__ftype=yabase_settings.FEATURED_SELECTION).exclude(origin=yabase_settings.RADIO_ORIGIN_KFM).order_by('featuredradio__order').all()
    else:
        selection_radios = qs.filter(featuredcontent__activated=True, featuredcontent__ftype=yabase_settings.FEATURED_SELECTION).order_by('featuredradio__order').all()

    selection_radios = list(selection_radios)
    # limit the number of editorial radios
    # shuffle the list in order not to choose always the same radios
    from random import shuffle
    shuffle(selection_radios)

    if hasattr(request, 'app_id') and request.app_id == yabase_settings.IPHONE_DEFAULT_APPLICATION_IDENTIFIER:
        selection_radios_count = yabase_settings.RADIO_SELECTION_VIEW_COUNT_IPHONE
    else:
        selection_radios_count = yabase_settings.RADIO_SELECTION_VIEW_COUNT

    selection_radios = selection_radios[:selection_radios_count]
    selection_radios_ids = [x.id for x in selection_radios]

    radio_data = []
    radio_list = []
    # results: first part
    s = 0
    for r in selection_radios[skip:(skip + limit)]:
        radio_data.append(r.as_dict(request_user=request.user))
        radio_list.append(r)
        s += 1

    # results: second part
    reco_skip = max(0, skip - selection_radios_count)
    reco_limit = max(0, limit - len(radio_data))

    request_user = None
    favorite_radio_ids = []
    if request.user is not None and request.user.is_authenticated():
        request_user = request.user
        favorite_radio_ids = Radio.objects.filter(radiouser__user=request_user, radiouser__favorite=True).values_list('id', flat=True)

    recommended_radios = []
    counter = 0
    for radio_id in recommendations:
            try:
                r = Radio.objects.get(id=radio_id)
            except Radio.DoesNotExist:
                continue

            if r.blacklisted:
                continue

            id_ok = r.id not in selection_radios_ids
            genre_ok = genre == '' or genre == r.genre  # get radio with the right genre
            creator_ok = r.creator != request_user
            favorite_ok = r.id not in favorite_radio_ids
            if id_ok and genre_ok and creator_ok and favorite_ok:
                recommended_radios.append(r)
                counter += 1
            if counter > (reco_skip + reco_limit):
                break

    r = 0
    for radio in recommended_radios[reco_skip:(reco_skip + reco_limit)]:
        radio_data.append(radio.as_dict(request_user=request.user))
        radio_list.append(radio)
        r += 1

    if len(radio_data) < limit:
        exclude_ids = selection_radios_ids + recommendations
        need_more = limit - len(radio_data)
        need_more_offset = max(0, skip - len(exclude_ids))
        qs = Radio.objects.ready_objects()
        if genre != '':
            qs = qs.filter(genre=genre)
        if request.user is not None and request.user.is_authenticated():
            # don't add user's radios
            # and the radios he has put in his favorites
            qs = qs.exclude(creator=request.user).exclude(radiouser__user=request.user, radiouser__favorite=True)
        extra_radios = qs.exclude(id__in=exclude_ids).order_by('-popularity_score', '-favorites')[need_more_offset:(need_more_offset + need_more)]
        e = 0
        for r in extra_radios:
            radio_data.append(r.as_dict(request_user=request.user))
            radio_list.append(r)
            e += 1


    params = {'skip': skip + limit}
    if recommendation_token is not None:
        params['token'] = recommendation_token
    if genre != '':
        params['genre'] = genre
    params_string = urllib.urlencode(params)
    next_url = reverse("yabase.views.radio_recommendations")
    next_url += '?%s' % params_string

    if internal:
        return radio_data, radio_list, next_url
    response = api_response(radio_data, limit=limit, offset=skip, next_url=next_url)
    return response

@csrf_exempt
def radio_recommendations(request):
    if not check_http_method(request, ['post', 'get']):
        return HttpResponse(status=405)
    check_api_key_Authentication(request)

    return radio_recommendations_process(request=request, internal=False)

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
    radio.set_picture(f)

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

    favorites = Radio.objects.filter(id=radio_id).values_list('favorites', flat=True)[0]
    res = {'success': True, 'favorites': favorites}
    return HttpResponse(json.dumps(res))

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

    favorites = Radio.objects.filter(id=radio_id).values_list('favorites', flat=True)[0]
    res = {'success': True, 'favorites': favorites}
    return HttpResponse(json.dumps(res))

@csrf_exempt
@check_api_key(methods=['POST',])
def radio_shared(request, radio_id):
    json_data = json.loads(request.raw_post_data)
    share_type = json_data['type']
    try:
        radio = Radio.objects.get(id=radio_id)
    except Radio.DoesNotExist:
        return HttpResponseNotFound()

    radio.shared(request.user, share_type)
    res = 'user %s has shared radio %s' % (request.user.get_profile().name, radio.name)
    return HttpResponse(res)


@csrf_exempt
@check_api_key(methods=['POST'])
def radio_likes(request, radio_uuid):
    radio = get_object_or_404(Radio, uuid=radio_uuid)
    payload = json.loads(request.raw_post_data)
    last_play_time = payload.get('last_play_time')
    # TODO use last_play_time to check song validity

    song = radio.current_song
    if song is not None:
        radio = song.playlist.radio
        if radio and not radio.is_live():
            song_user, _created = SongUser.objects.get_or_create(song=song, user=request.user)
            song_user.mood = yabase_settings.MOOD_LIKE
            song_user.save()

        # add like event in wall
        if radio is not None:
            WallEvent.objects.add_like_event(radio, song, request.user)

    if radio is not None:
        wm = WallManager()
        wm.add_event(event_type=WallManager.EVENT_LIKE, radio=radio, user=request.user)

    res = '%s (user) likes %s (song)\n' % (request.user, song)
    return HttpResponse(res)


# SONG USER
@csrf_exempt
@check_api_key(methods=['POST',])
def like_song(request, song_id):
    try:
        song = SongInstance.objects.get(id=song_id)
    except SongInstance.DoesNotExist:
        song = None

    if song is not None:
        radio = song.playlist.radio
        if radio and not radio.is_live():
            song_user, _created = SongUser.objects.get_or_create(song=song, user=request.user)
            song_user.mood = yabase_settings.MOOD_LIKE
            song_user.save()

        # add like event in wall
        if radio is not None:
            WallEvent.objects.add_like_event(radio, song, request.user)

            wm = WallManager()
            wm.add_event(event_type=WallManager.EVENT_LIKE, radio=radio, user=request.user)

    res = '%s (user) likes %s (song)\n' % (request.user, song)
    return HttpResponse(res)


@csrf_exempt
@check_api_key(methods=['POST'])
def post_message(request, radio_id):
    message = request.REQUEST.get('message')
    radio = get_object_or_404(Radio, uuid=radio_id)
    radio.post_message(request.user, message)

    wm = WallManager()
    wm.add_event(event_type=WallManager.EVENT_MESSAGE, radio=radio, user=request.user, message=message)

    return HttpResponse(status=200)


@check_api_key(methods=['PUT', 'DELETE'])
def delete_message(request, message_id):
    logger.debug('delete_message called with message_id %s' % (message_id))
    wall_event = get_object_or_404(WallEvent, pk=message_id)
    logger.debug('wall event found: %s' % (message_id))

    if request.user != wall_event.radio.creator:
        logger.debug('user is not the owner of the radio, delete is impossible')
        return HttpResponse(status=401)

    wm = WallManager()
    if wall_event.type == yabase_settings.EVENT_MESSAGE:
        existing_event = wm.find_existing_event(event_type=WallManager.EVENT_MESSAGE,
                                                radio_uuid=wall_event.radio.uuid,
                                                message=wall_event.text,
                                                date=wall_event.start_date,
                                                username=wall_event.user.username)
    elif wall_event.type == yabase_settings.EVENT_LIKE:
        existing_event = wm.find_existing_event(event_type=WallManager.EVENT_LIKE,
                                                radio_uuid=wall_event.radio.uuid,
                                                date=wall_event.start_date,
                                                username=wall_event.user.username,
                                                song=wall_event.song)

    if existing_event:
        print "------->"
        wm.remove_event(existing_event.get('event_id'))

    logger.debug('deleting message')
    wall_event.delete()

    logger.debug('logging information into metrics')
    yabase_signals.new_moderator_del_msg_activity.send(sender=request.user, user=request.user)

    logger.debug('ok, done')

    response = {'success': True}
    res = json.dumps(response)
    return HttpResponse(res)

@csrf_exempt
@check_api_key(methods=['POST',])
def report_message_as_abuse(request, message_id):
    logger.debug('report_message_as_abuse called with message_id %s' % (message_id))

    wall_event = get_object_or_404(WallEvent, pk=message_id)
    logger.debug('wall event found: %s' % (message_id))
    logger.debug(wall_event.type)

    logger.debug('reporting message message')
    wall_event.report_as_abuse(request.user)

    logger.debug('logging information into metrics')
    yabase_signals.new_moderator_abuse_msg_activity.send(sender=request.user, user=request.user, wall_event=wall_event)

    logger.debug('ok, done')
    response = {'success':True}
    res = json.dumps(response)
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


@csrf_exempt
def get_next_song(request, radio_id):
    logger.debug('get_next_song: radio = %s - start' % (radio_id))
    radio = get_object_or_404(Radio, uuid=radio_id)

    lock_id = "get_next_song_%d" % (radio.id)
    acquire_lock = lambda: cache.add(lock_id, "true", GET_NEXT_SONG_LOCK_EXPIRE)
    release_lock = lambda: cache.delete(lock_id)

    if not acquire_lock():
        logger.info('get_next_song locked for radio %d' % (radio.id))
        return HttpResponse('computing next songs already set', status=404)

    try:
        nextsong = radio.get_next_song()
        logger.debug('get_next_song: radio = %s - found next song' % (radio_id))
    finally:
        release_lock()

    if not nextsong:
        logger.error('get_next_song: radio = %s - cannot find next song' % (radio_id))
        return HttpResponse('cannot find next song', status=404)

    song = get_object_or_404(YasoundSong, id=nextsong.metadata.yasound_song_id)
    logger.debug('get_next_song: radio = %s - found yaref song (%s), finished!' % (radio_id, song.get_song_path()))
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

    user_id = request.REQUEST.get('user_id')
    if user_id is not None:
        try:
            user = User.objects.get(id=user_id)
            profile = user.get_profile()
            if profile:
                profile.authenticated()
            request.user = user
        except:
            pass

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
    user_id = request.REQUEST.get('user_id')
    if user_id is not None:
        try:
            user = User.objects.get(id=user_id)
            profile = user.get_profile()
            if profile:
                profile.authenticated()
            request.user = user
        except:
            pass

    if not check_http_method(request, ['post']):
        return HttpResponse(status=405)

    LISTENING_DURATION_PARAM_NAME = 'listening_duration'
    try:
        listening_duration = int(request.GET.get(LISTENING_DURATION_PARAM_NAME, 0))
    except:
        listening_duration = 0

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

@csrf_exempt
def radio_has_stopped(request, radio_uuid):
    if not check_http_method(request, ['post']):
        return HttpResponse(status=405)

    LISTENING_DURATION_PARAM_NAME = 'listening_duration'
    listening_duration = int(request.GET.get(LISTENING_DURATION_PARAM_NAME, 0))

    radio = get_object_or_404(Radio, uuid=radio_uuid)
    radio.stopped_playing(listening_duration)
    return HttpResponse('ok')

@csrf_exempt
def song_played(request, radio_uuid, songinstance_id):
    songinstance_id = int(songinstance_id)
    logger.info('song_played radio = %s song_instance_id = %d' % (radio_uuid, songinstance_id))
    if not check_http_method(request, ['post']):
        logger.info('song_played: wrong method')
        return HttpResponse(status=405)

    key = request.GET.get('key', 0)
    if key != settings.SCHEDULER_KEY:
        logger.info('song_played: wrong scheduler key (%s)' % key)
        return HttpResponseForbidden()

    async_song_played.delay(radio_uuid, songinstance_id)
    return HttpResponse('ok')

@csrf_exempt
def songs_started(request):
    if not check_http_method(request, ['post']):
        logger.info('songs_started: wrong method')
        return HttpResponse(status=405)

    payload = json.loads(request.raw_post_data)

    key = payload.get('key', 0)
    if key != settings.SCHEDULER_KEY:
        logger.info('songs_started: wrong scheduler key (%s)' % key)
        return HttpResponseForbidden()

    data = payload.get('data', None)
    if data is None:
        logger.info('songs_started: cannot get data')
        return HttpResponse(json.dumps({'success': False, 'error': 'bad data'}))
    async_songs_started.delay(data)
    return HttpResponse(json.dumps({'success': True}))

@check_api_key(methods=['GET',], login_required=False)
def get_current_song(request, radio_id):
    if request.user.is_anonymous():
        radio_uuid = Radio.objects.uuid_from_id(radio_id)
        if radio_uuid is not None:
            manager = AnonymousManager()
            anonymous_id = request.session.get('anonymous_id', uuid.uuid4().hex)
            request.session['anonymous_id'] = anonymous_id
            city_record = request_city_record(request)
            manager.upsert_anonymous(anonymous_id, radio_uuid, city_record)

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

    yabase_signals.buy_link.send(sender=request.user, radio=radio, user=request.user, song_instance=song_instance)

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

    if song_id:
        try:
            song_instance = SongInstance.objects.get(id=song_id)
            radio = Radio.objects.get(id=song_instance.playlist.radio.id)
            if request.user != radio.creator:
                return HttpResponse(status=401)
        except:
            logger.info('no radio')


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

    directory = mkdtemp(dir=settings.SHARED_TEMP_DIRECTORY)
    _path, extension = os.path.splitext(f.name)
    source = u'%s/s%s' % (directory, extension)
    source_f = open(source , 'wb')
    for chunk in f.chunks():
        source_f.write(chunk)
    source_f.close()

    if 'radio_uuid' in json_data or 'radio_id' in json_data:
        if 'radio_uuid' in json_data:
            radio = Radio.objects.get(uuid=json_data.get('radio_uuid'))
        else:
            radio = Radio.objects.get(id=json_data.get('radio_id'))

        if request.user != radio.creator:
            return HttpResponse(status=401)

        yabase_signals.new_animator_activity.send(sender=request.user,
                                              user=request.user,
                                              radio=radio,
                                              atype=yabase_settings.ANIMATOR_TYPE_UPLOAD_SONG)

    logger.info('importing song')

    process_upload_song.delay(filepath=source,
                              metadata=json_data,
                              convert=True,
                              song_id=song_id,
                              allow_unknown_song=True)

    res = 'upload OK for song: %s' % unicode(f.name)

    response_format = request.REQUEST.get('response_format', '')
    if response_format == 'json':
        response_data = {
            "name": f.name,
            "size": f.size,
            "type": f.content_type
        }
        # generate the json data
        response_data = json.dumps([response_data])
        # response type
        response_type = "application/json"
        if "text/html" in request.META["HTTP_ACCEPT"]:
            response_type = "text/html"
        return HttpResponse(response_data, mimetype=response_type)
    else:
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
            global_message = global_message + u'radio "%s" assigned to "%s"\n' % (unicode(radio), unicode(user))
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
@check_api_key(methods=['POST'])
def add_song(request, radio_id, playlist_index, yasound_song_id):
    radio_id = int(radio_id)
    playlist_index = int(playlist_index)
    yasound_song_id = int(yasound_song_id)
    radio = get_object_or_404(Radio, id=radio_id)
    radio.get_or_create_default_playlist()

    yabase_signals.new_animator_activity.send(sender=request.user,
                                              user=request.user,
                                              radio=radio,
                                              atype=yabase_settings.ANIMATOR_TYPE_ADD_SONG,
                                              details = {'yasound_song_id':yasound_song_id})

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

    try:
        metadata, _created = SongMetadata.objects.get_or_create(yasound_song_id=yasound_song_id,
                                                                name=name,
                                                                artist_name=artist_name,
                                                                album_name=album_name)
    except SongMetadata.MultipleObjectsReturned:
        # we have multiple candidates, let's take the first one
        metadata = SongMetadata.objects.filter(yasound_song_id=yasound_song_id,
                                               name=name,
                                               artist_name=artist_name,
                                               album_name=album_name)[0]

    song_instance = SongInstance.objects.create(playlist=playlist, metadata=metadata)
    if radio.ready == False:
        radio.ready = True
        radio.save()

    pm = ProgrammingHistory()
    event = pm.generate_event(event_type=ProgrammingHistory.PTYPE_ADD_FROM_YASOUND,
        user=radio.creator,
        radio=radio,
        status=ProgrammingHistory.STATUS_PENDING)

    details = {
        'name': song_instance.metadata.name,
        'artist': song_instance.metadata.artist_name,
        'album': song_instance.metadata.album_name,
    }
    pm.add_details_success(event, details)
    pm.success(event)

    res = dict(success=True, created=True, song_instance_id=song_instance.id)
    response = json.dumps(res)
    return HttpResponse(response)


@check_api_key(methods=['GET'], login_required=True)
def reject_song(request, song_id):
    song_instance = get_object_or_404(SongInstance, id=song_id)

    if request.user != song_instance.playlist.radio.creator:
        return HttpNotFound()

    logging.getLogger("yaapp.yabase.delete_song").info('rejecting song instance %s' % song_instance.id)
    radio = song_instance.playlist.radio
    radio.reject_song(song_instance)

    yabase_signals.new_animator_activity.send(sender=request.user,
                                              user=request.user,
                                              radio=radio,
                                              atype=yabase_settings.ANIMATOR_TYPE_REJECT_SONG,
                                              details={'song_instance':song_instance})

    res = {'success': True}
    response = json.dumps(res)
    return HttpResponse(response)


@check_api_key(methods=['GET',], login_required=False)
def song_instance_cover(request, song_instance_id):
    song_instance = get_object_or_404(SongInstance, id=song_instance_id)
    yasound_song = get_object_or_404(YasoundSong, id=song_instance.metadata.yasound_song_id)
    album = yasound_song.album
    if not album:
        return HttpResponseNotFound()
    url = album.large_cover_url
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
                return HttpResponsePermanentRedirect(url)

    if radio is None:
        raise Http404

    url = reverse('webapp_default_radio', args=[radio.uuid])
    return HttpResponsePermanentRedirect(url)


    radio_picture_absolute_url = absolute_url(radio.picture_url)
    flash_player_absolute_url = absolute_url('/media/player.swf')

    radio_url = radio.stream_url
    return render_to_response(template_name, {
        "radio": radio,
        "radio_url": radio_url,
        "listeners": radio.radiouser_set.filter(listening=True).count(),
        "fans": radio.radiouser_set.filter(favorite=True).count(),
        "new_page": '/app/#radio/%s' % (radio_uuid),
        "radio_picture_absolute_url": radio_picture_absolute_url,
        'flash_player_absolute_url': flash_player_absolute_url,
    }, context_instance=RequestContext(request))

def web_widget(request, radio_uuid, wtype=None, template_name='yabase/widget.html'):
    radio = None
    try:
        radio = Radio.objects.get(uuid=radio_uuid)
    except Radio.DoesNotExist:
        if len(radio_uuid) > 4:
            radios = Radio.objects.filter(uuid__startswith=radio_uuid)[:1]
            if radios.count() > 0:
                radio = radios[0]
                url = reverse('yabase.views.web_widget', args=[radio.uuid, wtype])
                return HttpResponsePermanentRedirect(url)

    if radio is None:
        raise Http404

    if wtype == 'large':
        template_name = 'yabase/widget_large.html'

    auto_play = request.REQUEST.get('autoplay', '')
    if auto_play != '1':
        auto_play = False

    radio_picture_absolute_url = absolute_url(radio.picture_url)
    radio_url = '%s%s' % (settings.YASOUND_STREAM_SERVER_URL, radio_uuid)
    return render_to_response(template_name, {
        "radio": radio,
        "radio_url": radio_url,
        "listeners": radio.radiouser_set.filter(listening=True).count(),
        "fans": radio.radiouser_set.filter(favorite=True).count(),
        "new_page": '/app/#radio/%s' % (radio_uuid),
        "radio_picture_absolute_url": radio_picture_absolute_url,
        "auto_play": auto_play,
    }, context_instance=RequestContext(request))


def web_song(request, radio_uuid, song_instance_id, template_name='yabase/song.html'):
    song_instance = get_object_or_404(SongInstance, id=song_instance_id)
    radio = get_object_or_404(Radio, uuid=radio_uuid)
    if song_instance.playlist.radio != radio:
        raise Http404

    url = reverse('webapp_default_radio_song', args=[radio.uuid, song_instance_id])
    return HttpResponseRedirect(url)

    radio_picture_absolute_url = absolute_url(radio.picture_url)
    radio_absolute_url =  absolute_url(reverse('yabase.views.web_listen', args=[radio_uuid]))
    radio_url = radio.stream_url
    flash_player_absolute_url = absolute_url('/media/player.swf')

    return render_to_response(template_name, {
        "radio": radio,
        "radio_url": radio_url,
        "listeners": radio.radiouser_set.filter(listening=True).count(),
        "fans": radio.radiouser_set.filter(favorite=True).count(),
        "new_page": '/app/#radio/%s' % (radio.uuid),
        "song": song_instance,
        "radio_station_url":radio_absolute_url,
        "radio_url" : radio_url,
        "radio_picture_absolute_url": radio_picture_absolute_url,
        'flash_player_absolute_url': flash_player_absolute_url,
    }, context_instance=RequestContext(request))

class WebAppView(View):
    """ Class based view for web app.
    """
    def _check_auth(self, request, radio_uuid=None):
        """
        centralized auth checking function,

        return True, None if ok or False, redirect page else
        """

        if self.app_name not in ['app', 'deezer', 'live']:
            raise Http404

        if settings.ANONYMOUS_ACCESS_ALLOWED == True:
            return True, None

        if not request.user.is_superuser:
            if request.user.groups.filter(name=account_settings.GROUP_NAME_BETATEST).count() == 0:
                if radio_uuid:
                    return False, HttpResponseRedirect(reverse('yabase.views.web_listen', args=[radio_uuid]))
                raise Http404
        return True, None

    def _get_push_url(self, request):
        """
        return absolute url (with port) of push server
        """

        host = request.META['HTTP_HOST']
        protocol = settings.DEFAULT_HTTP_PROTOCOL
        if ':' in host:
            host = host[:host.find(':')]

        url = '%s://%s:%d/' % (protocol, host, settings.YASOUND_PUSH_PORT)
        return url

    def _ajax_success(self):
        data = {
            'success': True
        }
        response = json.dumps(data)
        return HttpResponse(response, mimetype='application/json')

    def _ajax_error(self, errors):
        data = {
            'success': False,
            'errors': errors
        }
        response = json.dumps(data)
        return HttpResponse(response, mimetype='application/json')

    def home(self, request, context, *args, **kwargs):
        context['g_page'] = 'home'
        context['mustache_template'] = 'yabase/app/home/homePage.mustache'
        return context, 'yabase/app/static.html'

    def radio(self, request, context, *args, **kwargs):
        wm = WallManager()
        radio = get_object_or_404(Radio, uuid=context['current_uuid'])
        radio.favorite = radio.is_favorite(request.user)
        context['radio'] = radio
        context['ignore_radio_cookie'] = True
        if radio.current_song:
            context['yasound_song'] = YasoundSong.objects.get(id=radio.current_song.metadata.yasound_song_id)
        context['radio_picture_absolute_url'] = absolute_url(radio.picture_url)
        wall_events = list(wm.events_for_radio(radio.uuid, limit=10))
        context['wall_events'] = wall_events
        context['radio_picture_absolute_url'] = absolute_url(radio.picture_url)
        context['flash_player_absolute_url'] = absolute_url('/media/player.swf')
        context['radio_absolute_url'] = absolute_url(reverse('webapp_default_radio', args=[radio.uuid]))

        bdata = {
            'wall_events': wall_events,
            'radio': [radio.as_dict(request.user)],
        }
        context['bdata'] = json.dumps(bdata, cls=MongoAwareEncoder)

        return context, 'yabase/app/radio/radioPage.html'

    def song(self, request, context, *args, **kwargs):
        radio = get_object_or_404(Radio, uuid=context['current_uuid'])
        song_instance = get_object_or_404(SongInstance, id=kwargs['song_id'])
        radio.favorite = radio.is_favorite(request.user)
        context['radio'] = radio
        context['ignore_radio_cookie'] = True
        if radio.current_song:
            context['yasound_song'] = YasoundSong.objects.get(id=radio.current_song.metadata.yasound_song_id)
        context['radio_picture_absolute_url'] = absolute_url(radio.picture_url)
        wall_events = WallEvent.objects.select_related('user', 'user__userprofile', 'radio').filter(radio=radio).order_by('-start_date')[:15]
        context['wall_events'] = wall_events
        context['radio_picture_absolute_url'] = absolute_url(radio.picture_url)
        context['flash_player_absolute_url'] = absolute_url('/media/player.swf')
        context['song_instance_absolute_url'] = absolute_url(reverse('webapp_default_radio_song', args=[radio.uuid, song_instance.id]))

        bdata = {
            'wall_events': [wall_event.as_dict() for wall_event in wall_events],
            'radio': [radio.as_dict(request.user)],
        }
        context['bdata'] = json.dumps(bdata, cls=MongoAwareEncoder)
        context['song_instance'] = song_instance
        context['radio_station_url'] = absolute_url(reverse('webapp_default_radio', args=[radio.uuid]))
        return context, 'yabase/app/radio/songPage.html'

    def search(self, request, context, *args, **kwargs):
        query = kwargs['query']
        if len(query) > 0:
            query = query[:25]

        rm = RadiosManager()
        result = rm.search(query)
        context['submenu_number'] = 6
        context['query'] = query
        return context, 'yabase/app/searchPage.html'

    def top(self, request, context, *args, **kwargs):
        genre = ''
        if 'genre' in kwargs:
            genre = 'style_%s' % (kwargs['genre'])
        radios, next_url = most_active_radios(request, internal=True, genre=genre)
        context['radios'] = radios
        context['next_url'] = next_url
        context['base_url'] = reverse('yabase.views.most_active_radios')
        context['bdata'] = json.dumps([radio.as_dict(request.user) for radio in radios], cls=MongoAwareEncoder)
        context['submenu_number'] = 2
        context['mustache_template'] = 'yabase/app/top/topRadiosPage.mustache'
        return context, 'yabase/app/static.html'

    def legal(self, request, context, *args, **kwargs):
        context['mustache_template'] = 'yabase/app/static/legal.mustache'
        return context, 'yabase/app/static.html'

    def contact(self, request, context, *args, **kwargs):
        context['mustache_template'] = 'yabase/app/static/contact.mustache'
        return context, 'yabase/app/static.html'

    def about(self, request, context, *args, **kwargs):
        context['mustache_template'] = 'yabase/app/static/about.mustache'
        return context, 'yabase/app/static.html'

    def press(self, request, context, *args, **kwargs):
        context['mustache_template'] = 'yabase/app/static/press.mustache'
        return context, 'yabase/app/static.html'

    def jobs(self, request, context, *args, **kwargs):
        context['mustache_template'] = 'yabase/app/static/jobs.mustache'
        return context, 'yabase/app/static.html'

    def favorites(self, request, context, *args, **kwargs):
        context['submenu_number'] = 4
        context['mustache_template'] = 'yabase/app/favorites/favoritesPage.mustache'
        return context, 'yabase/app/static.html'

    def friends(self, request, context, *args, **kwargs):
        context['submenu_number'] = 3
        context['mustache_template'] = 'yabase/app/friends/friendsPage.mustache'
        return context, 'yabase/app/static.html'

    def listeners(self, request, context, *args, **kwargs):
        context['mustache_template'] = 'yabase/app/radio/listenersPage.mustache'
        return context, 'yabase/app/static.html'

    def fans(self, request, context, *args, **kwargs):
        context['mustache_template'] = 'yabase/app/radio/fansPage.mustache'
        return context, 'yabase/app/static.html'

    def profile(self, request, context, *args, **kwargs):
        return context, 'yabase/webapp.html'

    def programming(self, request, context, *args, **kwargs):
        radio_uuid = context['current_uuid']
        radio = get_object_or_404(Radio, uuid=radio_uuid)
        if radio.creator != request.user:
            return HttpResponse(status=401)
        return context, 'yabase/webapp.html'

    def notifications(self, request, context, *args, **kwargs):
        if request.user.is_authenticated():
            m = NotificationsManager()
            notifications = list(m.notifications_for_recipient(request.user.id, count=25, read_status='unread'))
            context['notifications'] = notifications
            context['bdata'] = json.dumps([notification for notification in notifications], cls=MongoAwareEncoder)
            context['g_page'] = 'notifications'
        return context, 'yabase/app/notifications/notificationsPage.html'

    def radios(self, request, context, *args, **kwargs):
        context['submenu_number'] = 5
        return context, 'yabase/webapp.html'

    def new_radio(self, request, context, *args, **kwargs):
        if not request.user.is_authenticated():
            return HttpResponseRedirect(reverse('webapp', args=[self.app_name]))

        if request.method == 'POST':
            profile = request.user.get_profile()
            if not profile.permissions.create_radio:
                if request.is_ajax():
                    data = {
                        'success': False,
                        'message': unicode(_('You are not allowed to create a radio'))
                    }
                    return api_response(data)
                else:
                    return HttpResponseRedirect(reverse('webapp', args=[self.app_name]))

            country = request_country(request)
            if not yageoperm_utils.can_create_radio(request.user, country):
                if request.is_ajax():
                    data = {
                        'success': False,
                        'message': unicode(_('This feature is not yet available for your country'))
                    }
                    return api_response(data)
                else:
                    return HttpResponseRedirect(reverse('webapp', args=[self.app_name]))

            form = NewRadioForm(request.POST, request.FILES)
            if form.is_valid():
                radio = form.save(commit=False)
                radio.creator = request.user
                radio.save()
                form.save_m2m()
                if request.is_ajax():
                    data = {
                        'success': True,
                        'url': 'radio/%s/programming/' % (radio.uuid),
                        'upload_photo_url': reverse('yabase.views.radio_picture', args=[radio.uuid])
                    }
                    response = json.dumps(data)
                    return HttpResponse(response, mimetype='application/json')
                return HttpResponseRedirect(reverse('webapp_programming', args=[self.app_name, radio.uuid]))
            else:
                if request.is_ajax():
                    return self._ajax_error(form.errors)
        else:
            form = NewRadioForm()

        context['submenu_number'] = 5
        context['form'] = form
        return context, 'yabase/webapp.html'

    def signup(self, request, context, *args, **kwargs):
        if request.method == 'POST':
            form = WebAppSignupForm(request.POST)
            if form.is_valid():
                form.save()
                if request.is_ajax():
                    data = {
                        'success': True
                    }
                    response = json.dumps(data)
                    return HttpResponse(response, mimetype='application/json')
                else:
                    return HttpResponseRedirect(reverse('webapp', args=[self.app_name]))
            else:
                if request.is_ajax():
                    data = {
                        'success': False,
                        'errors': form.errors
                    }
                    response = json.dumps(data)
                    return HttpResponse(response, mimetype='application/json')
                else:
                    context['signup_form'] = form
        return context, 'yabase/app/signup/signup.html'

    def login(self, request, context, *args, **kwargs):
        if request.method == 'POST':
            form = LoginForm(request.POST)
            if form.is_valid() and form.login(request):
                if request.is_ajax():
                    return self._ajax_success()
                else:
                    return HttpResponseRedirect(reverse('webapp', args=[self.app_name]))
            else:
                if request.is_ajax():
                    return self._ajax_error(form.errors)
                else:
                    context['signup_form'] = form
        return context, 'yabase/app/login/login.html'

    def settings(self, request, context, *args, **kwargs):
        if not request.user.is_authenticated():
            return HttpResponseRedirect(reverse('webapp_login', args=[self.app_name]))

        if request.method == 'POST':
            my_informations_form = MyInformationsForm(instance=request.user.get_profile())
            my_accounts_form = MyAccountsForm(instance=request.user.get_profile())
            my_notifications_form = MyNotificationsForm(user_profile=request.user.get_profile())

            action = request.REQUEST.get('action')
            if action == 'my_informations':
                my_informations_form = MyInformationsForm(request.POST, request.FILES, instance=request.user.get_profile())
                if my_informations_form.is_valid():
                    my_informations_form.save()
                    if request.is_ajax():
                        return self._ajax_success()
                    return HttpResponseRedirect(reverse('webapp_settings', args=[self.app_name]))
                else:
                    if request.is_ajax():
                        return self._ajax_error(my_informations_form.errors)
            elif action == 'my_accounts':
                my_accounts_form = MyAccountsForm(request.POST, instance=request.user.get_profile())
                if my_accounts_form.is_valid():
                    my_accounts_form.save()
                    if request.is_ajax():
                        return self._ajax_success()
                    return HttpResponseRedirect(reverse('webapp_settings', args=[self.app_name]))
                else:
                    if request.is_ajax():
                        return self._ajax_error(my_accounts_form.errors)
            elif action == 'my_notifications':
                my_notifications_form = MyNotificationsForm(request.user.get_profile(), request.POST)
                if my_notifications_form.is_valid():
                    my_notifications_form.save()
                    if request.is_ajax():
                        return self._ajax_success()
                    return HttpResponseRedirect(reverse('webapp_settings', args=[self.app_name]))
                else:
                    if request.is_ajax():
                        return self._ajax_error(my_notifications_form.errors)

            context['my_informations_form'] = my_informations_form
            context['my_accounts_form'] = my_accounts_form
            context['my_notifications_form'] = my_notifications_form

        return context, 'yabase/webapp.html'

    def edit_radio(self, request, context, *args, **kwargs):
        if not request.user.is_authenticated():
            return HttpResponseRedirect(reverse('webapp', args=[self.app_name]))

        if request.method == 'POST':
            action = request.REQUEST.get('action')
            if action == 'radio_settings':
                uuid = request.REQUEST.get('uuid', '')
                radio = get_object_or_404(Radio, uuid=uuid)
                if radio.creator != request.user:
                    return HttpResponse(status=401)
                form = SettingsRadioForm(request.POST, request.FILES, instance=radio)
                if form.is_valid():
                    form.save()
                    if request.is_ajax():
                        return self._ajax_success()
                    return HttpResponseRedirect(reverse('webapp_edit_radio', args=[self.app_name, uuid]))
                else:
                    if request.is_ajax():
                        return self._ajax_error(form.errors)

        return context, 'yabase/webapp.html'

    def _default_radio_uuid(self, user):
        radios = Radio.objects.ready_objects().filter(featuredcontent__activated=True, featuredcontent__ftype=yabase_settings.FEATURED_SELECTION).order_by('featuredradio__order')
        try:
            return radios.values_list('uuid', flat=True)[0]
        except:
            pass
        return None

    def get(self, request, radio_uuid=None, user_id=None, template_name='yabase/webapp.html', page='home', app_name='app', *args, **kwargs):
        """
        GET method dispatcher. Calls related methods for specific pages
        """
        if request.path.startswith('/app/'):
            return HttpResponseRedirect(request.get_full_path()[len('/app'):])

        self.app_name = app_name
        authorized, redirection = self._check_auth(request, radio_uuid)
        if not authorized:
            return redirection

        notification_count = 0

        my_informations_form = None
        my_accounts_form = None
        my_notifications_form = None
        display_associate_facebook = False
        display_associate_twitter = False

        show_welcome_popup = False
        hd_enabled = False
        hd_expiration_date = None

        twitter_referal = False
        email_referal = False

        is_jm_radio = radio_uuid == settings.JM_RADIO

        next = ''
        referal = request.REQUEST.get('referal', '')
        referal_username = request.REQUEST.get('username', '')
        if referal == 'twitter' and referal_username != '':
            next = '?referal=twitter%%26username=%s' % (referal_username)
        if referal == 'email' and referal_username != '':
            next = '?referal=email%%26username=%s' % (referal_username)


        if request.user.is_authenticated():
            if app_name == 'app':
                twitter_referal = absolute_url(reverse('webapp_default_signup')) + '?referal=twitter&username=' + request.user.username
                email_referal = absolute_url(reverse('webapp_default_signup')) + '?referal=email&username=' + request.user.username
            else:
                twitter_referal = absolute_url(reverse('webapp_signup', args=[app_name])) + '?referal=twitter&username=' + request.user.username
                email_referal = absolute_url(reverse('webapp_signup', args=[app_name])) + '?referal=email&username=' + request.user.username

            user_profile = request.user.get_profile()

            if referal == 'twitter' and user_profile.twitter_uid is not None:
                inviter_profile = UserProfile.objects.get(user__username=referal_username)
                if inviter_profile.id != user_profile.id:
                    if not inviter_profile.has_invited_twitter_friend(user_profile.twitter_uid):
                        inviter_profile.invite_twitter_friends([user_profile.twitter_uid])
                        logger.debug('new invitation!')
                        async_check_for_invitation.delay(InvitationsManager.TYPE_TWITTER, user_profile.twitter_uid)
                else:
                    logger.debug('referal already taken into account')

            if referal == 'email' and user_profile.user.email is not None:
                inviter_profile = UserProfile.objects.get(user__username=referal_username)
                if inviter_profile.id != user_profile.id:
                    if not inviter_profile.has_invited_email_friend(user_profile.user.email):
                        inviter_profile.invite_email_friends([user_profile.user.email])
                        logger.debug('new invitation!')
                        async_check_for_invitation.delay(InvitationsManager.TYPE_EMAIL, user_profile.user.email)
                else:
                    logger.debug('referal already taken into account')

            hd_enabled = user_profile.permissions.hd.is_set
            hd_expiration_date = user_profile.hd_expiration_date

            if user_profile.web_preferences().get('hide_welcome_popup'):
                show_welcome_popup = False
            else:
                show_welcome_popup = True

            user_profile.set_web_preferences('hide_welcome_popup', True)

            nm = NotificationsManager()
            notification_count = nm.unread_count(request.user.id)

            display_associate_facebook = not request.user.get_profile().facebook_enabled
            display_associate_twitter = not request.user.get_profile().twitter_enabled
            my_informations_form = MyInformationsForm(instance=request.user.get_profile())
            my_accounts_form = MyAccountsForm(instance=request.user.get_profile())
            my_notifications_form = MyNotificationsForm(user_profile=request.user.get_profile())

        else:
            user_profile = None

        push_url = self._get_push_url(request)
        enable_push = settings.ENABLE_PUSH

        facebook_share_picture = absolute_url(settings.FACEBOOK_SHARE_PICTURE)
        facebook_share_link = absolute_url(reverse('webapp_default'))

        if app_name != 'deezer':
            facebook_channel_url = absolute_url(reverse('facebook_channel_url'))
        else:
            facebook_channel_url = absolute_url(reverse('deezer_facebook_channel_url'))

        genre_form = RadioGenreForm()

        has_radios = False
        if request.user.is_authenticated():
            has_radios = request.user.get_profile().has_radios


        if not radio_uuid:
            radio_uuid = self._default_radio_uuid(request.user)

        connected_users = fast_connected_users_by_distance(request, internal=True)

        root = get_root(request, app_name)
        alternate_language_urls = get_alternate_language_urls(request)

        sound_player = 'soundmanager'
        if app_name == 'deezer' and settings.LOCAL_MODE == False:
            sound_player = 'deezer'

        announcement = Announcement.objects.get_current_announcement()


        context = {
            'alternate_language_urls': alternate_language_urls,
            'user_id' : user_id,
            'is_jm_radio': is_jm_radio,
            'jm_radio_uuid': settings.JM_RADIO,
            'push_url': push_url,
            'enable_push': enable_push,
            'current_uuid': radio_uuid,
            'ignore_radio_cookie': False,
            'facebook_app_id': settings.FACEBOOK_APP_ID,
            'facebook_share_picture': facebook_share_picture,
            'facebook_share_link': facebook_share_link,
            'facebook_channel_url': facebook_channel_url,
            'genres': yabase_settings.RADIO_STYLE_CHOICES,
            'user_profile': user_profile,
            'import_itunes_form': ImportItunesForm(user=request.user),
            'notification_count': notification_count,
            'genre_form': genre_form,
            'has_radios': has_radios,
            'submenu_number': 1,
            'display_associate_facebook': display_associate_facebook,
            'display_associate_twitter': display_associate_twitter,
            'my_informations_form': my_informations_form,
            'my_accounts_form': my_accounts_form,
            'my_notifications_form': my_notifications_form,
            'minutes': get_global_minutes(),
            'deezer_channel_url': absolute_url(reverse('deezer_channel_https')),
            'deezer_app_id': settings.DEEZER_APP_ID,
            'connected_users': connected_users,
            'sound_player': sound_player,
            'root': root,
            'app_name': app_name,
            'show_welcome_popup': show_welcome_popup,
            'hd_enabled': hd_enabled,
            'hd_expiration_date': hd_expiration_date,
            'twitter_referal': twitter_referal,
            'email_referal': email_referal,
            'referal_username': referal_username,
            'announcement': announcement,
            'next': next,
        }

        if hasattr(self, page):
            handler = getattr(self, page)
            result = handler(request, context, *args, **kwargs)
            if type(result) == type(()):
                context, template_name = result[0], result[1]
            else:
                return result

        return render_to_response(template_name, context, context_instance=RequestContext(request))

    @method_decorator(csrf_exempt)
    def post(self, request, radio_uuid=None, query=None, user_id=None, template_name='yabase/webapp.html', page='home', app_name='app', *args, **kwargs):
        """
        POST method dispatcher
        """
        self.app_name = app_name
        self._check_auth(request, radio_uuid)

        user_profile = None
        notification_count = 0
        push_url = self._get_push_url(request)
        enable_push = settings.ENABLE_PUSH

        my_informations_form = None
        my_accounts_form = None
        my_notifications_form = None
        display_associate_facebook = False
        display_associate_twitter = False
        if request.user.is_authenticated():
            display_associate_facebook = not request.user.get_profile().facebook_enabled
            display_associate_twitter = not request.user.get_profile().twitter_enabled

        has_radios = False

        facebook_share_picture = absolute_url(settings.FACEBOOK_SHARE_PICTURE)
        facebook_share_link = absolute_url(reverse('webapp', args=[self.app_name]))

        hd_enabled = False
        hd_expiration_date = None

        next = ''
        referal = request.REQUEST.get('referal', '')
        referal_username = request.REQUEST.get('username', '')
        if referal == 'twitter' and referal_username != '':
            next = '?referal=twitter%%26username=%s' % (referal_username)
        if referal == 'email' and referal_username != '':
            next = '?referal=email%%26username=%s' % (referal_username)

        twitter_referal = False
        email_referal = False

        is_jm_radio = radio_uuid == settings.JM_RADIO

        if request.user.is_authenticated():
            if app_name == 'app':
                twitter_referal = absolute_url(reverse('webapp_default_signup')) + '?referal=twitter&username=' + request.user.username
                email_referal = absolute_url(reverse('webapp_default_signup')) + '?referal=email&username=' + request.user.username
            else:
                twitter_referal = absolute_url(reverse('webapp_signup', args=[app_name])) + '?referal=twitter&username=' + request.user.username
                email_referal = absolute_url(reverse('webapp_signup', args=[app_name])) + '?referal=email&username=' + request.user.username

            user_profile = request.user.get_profile()

            if referal == 'twitter' and user_profile.twitter_uid is not None:
                inviter_profile = UserProfile.objects.get(user__username=referal_username)
                if inviter_profile.id != user_profile.id:
                    if not inviter_profile.has_invited_twitter_friend(user_profile.twitter_uid):
                        inviter_profile.invite_twitter_friends([user_profile.twitter_uid])
                        logger.debug('new invitation!')
                        async_check_for_invitation.delay(InvitationsManager.TYPE_TWITTER, user_profile.twitter_uid)
                else:
                    logger.debug('referal already taken into account')

            if referal == 'email' and user_profile.user.email is not None:
                inviter_profile = UserProfile.objects.get(user__username=referal_username)
                if inviter_profile.id != user_profile.id:
                    if not inviter_profile.has_invited_email_friend(user_profile.user.email):
                        inviter_profile.invite_email_friends([user_profile.user.email])
                        logger.debug('new invitation!')
                        async_check_for_invitation.delay(InvitationsManager.TYPE_EMAIL, user_profile.user.email)
                else:
                    logger.debug('referal already taken into account')



            user_profile  = request.user.get_profile()
            nm = NotificationsManager()
            notification_count = nm.unread_count(request.user.id)

            hd_enabled = user_profile.permissions.hd.is_set
            hd_expiration_date = user_profile.hd_expiration_date

            has_radios = False
            if request.user.is_authenticated():
                has_radios = request.user.get_profile().has_radios

            if user_profile.web_preferences().get('hide_welcome_popup'):
                show_welcome_popup = False
            else:
                show_welcome_popup = True

            user_profile.set_web_preferences('hide_welcome_popup', True)

        import_itunes_form = ImportItunesForm()


        action = request.REQUEST.get('action')
        if action == 'import_itunes':
            import_itunes_form = ImportItunesForm(request.user, request.POST)
            if import_itunes_form.is_valid():
                import_itunes_form.save()
                if request.is_ajax():
                    return self._ajax_success();
            else:
                if request.is_ajax():
                    return self._ajax_error(import_itunes_form.errors)

        if app_name != 'deezer':
            facebook_channel_url = absolute_url(reverse('facebook_channel_url'))
        else:
            facebook_channel_url = absolute_url(reverse('deezer_facebook_channel_url'))

        genre_form = RadioGenreForm()

        root = get_root(request, app_name)

        sound_player = 'soundmanager'
        if app_name == 'deezer':
            sound_player = 'deezer'


        show_welcome_popup = True
        alternate_language_urls = get_alternate_language_urls(request)

        context = {
            'alternate_language_urls': alternate_language_urls,
            'user_id' : user_id,
            'is_jm_radio': is_jm_radio,
            'jm_radio_uuid': settings.JM_RADIO,
            'push_url': push_url,
            'enable_push': enable_push,
            'current_uuid': radio_uuid,
            'facebook_app_id': settings.FACEBOOK_APP_ID,
            'facebook_share_picture': facebook_share_picture,
            'facebook_share_link': facebook_share_link,
            'facebook_channel_url': facebook_channel_url,
            'user_profile': user_profile,
            'import_itunes_form': import_itunes_form,
            'notification_count': notification_count,
            'submenu_number': 1,
            'genres': yabase_settings.RADIO_STYLE_CHOICES,
            'has_radios': has_radios,
            'genre_form': genre_form,
            'display_associate_facebook': display_associate_facebook,
            'display_associate_twitter': display_associate_twitter,
            'my_informations_form': my_informations_form,
            'my_accounts_form': my_accounts_form,
            'my_notifications_form': my_notifications_form,
            'minutes': get_global_minutes(),
            'deezer_channel_url': absolute_url(reverse('deezer_channel_https')),
            'deezer_app_id': settings.DEEZER_APP_ID,
            'sound_player': sound_player,
            'root': root,
            'app_name': app_name,
            'show_welcome_popup': show_welcome_popup,
            'hd_enabled': hd_enabled,
            'hd_expiration_date': hd_expiration_date,
            'twitter_referal': twitter_referal,
            'email_referal': email_referal,
            'referal_username': referal_username,
            'next': next,
        }

        if hasattr(self, page):
            handler = getattr(self, page)
            result = handler(request, context, *args, **kwargs)
            if type(result) == type(()):
                context, template_name = result[0], result[1]
            else:
                return result

        return render_to_response(template_name, context, context_instance=RequestContext(request))

def radios(request, template_name='web/radios.html'):
    return render_to_response(template_name, {
    }, context_instance=RequestContext(request))

@login_required
def web_myradio(request, radio_uuid=None, template_name='web/my_radio.html'):
    radio = None
    if not uuid:
        radios = request.user.get_profile().own_radios(only_ready_radios=True)[0:1]
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
    users = User.objects.all()[:1]
    YasoundSong.objects.all()[:1]

    # fake stuff to check if database is ok
    _count = users.count()
    return HttpResponse('OK')


@check_api_key(methods=['PUT', 'DELETE', 'POST'])
def delete_song_instance(request, song_instance_id, event=None):
    song = get_object_or_404(SongInstance, pk=song_instance_id)

    if request.user != song.playlist.radio.creator:
        return HttpResponse(status=401)

    details = {
        'name': song.metadata.name,
        'artist': song.metadata.artist_name,
        'album': song.metadata.album_name,
    }

    logging.getLogger("yaapp.yabase.delete_song").info('deleting song instance %s' % song.id)
    song.delete()

    # if radio has no more songs, set ready to False
    radio = song.playlist.radio

    pm = ProgrammingHistory()
    if event is None:
        event = pm.generate_event(event_type=ProgrammingHistory.PTYPE_REMOVE_FROM_PLAYLIST,
            user=radio.creator,
            radio=radio,
            status=ProgrammingHistory.STATUS_PENDING)
        pm.success(event)

    pm.add_details_success(event, details)

    yabase_signals.new_animator_activity.send(sender=request.user,
                                              user=request.user,
                                              radio=radio,
                                              atype=yabase_settings.ANIMATOR_TYPE_DELETE_SONG,
                                              details={'song_instance':song})

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

@csrf_exempt
@check_api_key(methods=['POST',])
def radio_broadcast_message(request, radio_uuid):
    radio = get_object_or_404(Radio, uuid=radio_uuid)
    if radio.creator != request.user:
        return HttpResponse(status=403)

    message = request.REQUEST.get('message')
    radio.broadcast_message(message)
    return HttpResponse('OK')


@check_api_key(methods=['GET'], login_required=False)
def most_active_radios(request, internal=False, genre=''):
    limit = int(request.GET.get('limit', yabase_settings.MOST_ACTIVE_RADIOS_LIMIT))
    skip = int(request.GET.get('skip', 0))
    offset = int(request.GET.get('offset', 0))

    if skip == 0 and offset > 0:
        skip = offset

    if genre == '':
        genre = request.GET.get('genre', '')

    if genre != '':
        qs = Radio.objects.filter(genre=genre)
    else:
        qs = Radio.objects

    qs = qs.exclude(deleted=True).exclude(blacklisted=True)
    if is_iphone(request) or is_deezer(request):
        qs = qs.exclude(origin=yabase_settings.RADIO_ORIGIN_KFM)

    total_count = qs.count()
    radios = qs.order_by('-popularity_score', '-favorites')[skip:(skip + limit)]

    params = {'skip': skip + limit}
    if genre != '':
        params['genre'] = genre
    params_string = urllib.urlencode(params)
    next_url = reverse("yabase.views.most_active_radios")
    next_url += '?%s' % params_string

    if internal:
        return radios, next_url

    radio_data = []
    for r in radios:
        radio_data.append(r.as_dict(request_user=request.user))


    response = api_response(radio_data, total_count, limit=limit, offset=skip, next_url=next_url)
    return response

@csrf_exempt
@check_api_key(methods=['POST',], login_required=False)
def ping(request):
    radio_uuid = request.REQUEST.get('radio_uuid')
    if request.user.is_authenticated():
        profile = request.user.get_profile()
        profile.authenticated()

        radio = get_object_or_404(Radio, uuid=radio_uuid)
        radio_user, _created = RadioUser.objects.get_or_create(radio=radio, user=request.user)
        radio_user.connected = True
        radio_user.listening = True
        radio_user.save()
    else:
        manager = AnonymousManager()
        anonymous_id = request.session.get('anonymous_id', uuid.uuid4().hex)
        request.session['anonymous_id'] = anonymous_id
        city_record = request_city_record(request)
        manager.upsert_anonymous(anonymous_id, radio_uuid, city_record)

    return HttpResponse('OK')

@check_api_key(methods=['GET',], login_required=False)
def similar_radios(request, radio_uuid):
    radio = get_object_or_404(Radio, uuid=radio_uuid)
    similar_radios = radio.similar_radios()

    data = []
    for radio in similar_radios:
        data.append(radio.as_dict(request_user=request.user))
    return api_response(data)

#
#    programming
#
def programming_response(request, radio):
    limit = int(request.REQUEST.get('limit', 25))
    offset = int(request.REQUEST.get('offset', 0))
    artists = request.REQUEST.getlist('artist')
    albums = request.REQUEST.getlist('album')
    tracks = radio.programming(artists, albums)
    total_count = tracks.count()
    response = api_response(list(tracks[offset:offset+limit]), total_count, limit=limit, offset=offset)
    return response

def programming_artists_response(request, radio):
    artists = radio.programming_artists()
    total_count = artists.count()
    response = api_response(list(artists), total_count)
    return response

def programming_albums_response(request, radio):
    artists = request.REQUEST.getlist('artist')
    albums = radio.programming_albums(artists)
    total_count = albums.count()
    response = api_response(list(albums), total_count)
    return response

@csrf_exempt
@check_api_key(methods=['GET', 'POST',  'DELETE', ], login_required=True)
def my_programming(request, radio_uuid, song_instance_id=None):
    radio = get_object_or_404(Radio, uuid=radio_uuid)
    if request.user != radio.creator:
        return HttpResponse(status=401)

    if song_instance_id is not None and request.method == 'DELETE':
        return delete_song_instance(request, song_instance_id)

    if request.method == 'POST':
        action = request.REQUEST.get('action', '')
        if action == 'delete':
            artists = request.REQUEST.getlist('artist')
            albums = request.REQUEST.getlist('album')
            tracks = radio.programming(artists, albums)

            pm = ProgrammingHistory()
            event = pm.generate_event(event_type=ProgrammingHistory.PTYPE_REMOVE_FROM_PLAYLIST,
                user=radio.creator,
                radio=radio,
                status=ProgrammingHistory.STATUS_PENDING)

            for track in tracks:
                delete_song_instance(request, track.get('id'), event=event)
            pm.finished(event)

    response = programming_response(request, radio)
    return response

@check_api_key(methods=['GET', 'POST'], login_required=True)
def my_programming_artists(request, radio_uuid):
    radio = get_object_or_404(Radio, uuid=radio_uuid)
    if request.method == 'GET':
        response = programming_artists_response(request, radio)
        return response
    elif request.method == 'POST':
        if request.user != radio.creator:
            return HttpResponse(status=401)
        data = json.loads(request.raw_post_data)
        action = data.get('action')
        if action == 'delete':
            artist_name = data.get('name')
            tracks = radio.programming(artists=[artist_name])
            for track in tracks:
                delete_song_instance(request, track.get('id'))
            res = {'success': True}
            return HttpResponse(json.dumps(res))
    raise Http404

@check_api_key(methods=['GET', 'POST'], login_required=True)
def my_programming_albums(request, radio_uuid=None):
    radio = get_object_or_404(Radio, uuid=radio_uuid)
    if request.method == 'GET':
        response = programming_albums_response(request, radio)
        return response
    elif request.method == 'POST':
        if request.user != radio.creator:
            return HttpResponse(status=401)
        data = json.loads(request.raw_post_data)
        action = data.get('action')
        if action == 'delete':
            album_name = data.get('name')
            tracks = radio.programming(albums=[album_name])
            for track in tracks:
                delete_song_instance(request, track.get('id'))
            res = {'success': True}
            return HttpResponse(json.dumps(res))


@csrf_exempt
@check_api_key(methods=['GET', 'POST', ], login_required=True)
def my_programming_yasound_songs(request, radio_uuid):
    radio = get_object_or_404(Radio, uuid=radio_uuid)
    if request.user != radio.creator:
        return HttpResponse(status=401)

    if request.method == 'GET':
        limit = int(request.REQUEST.get('limit', 25))
        offset = int(request.REQUEST.get('offset', 0))
        name = request.REQUEST.get('name', '').lower()
        artist = request.REQUEST.get('artist', '').lower()
        album = request.REQUEST.get('album', '').lower()
        fuzzy = request.REQUEST.get('fuzzy', '').lower()
        data = []
        total_count = 0

        if name == '' and artist == '' and album == '':
            pass
        else:
            qs = YasoundSong.objects.all()
            if artist != '':
                qs = qs.filter(artist_name_simplified=artist)
            if name != '':
                if artist == '':
                    qs = qs.filter(name_simplified=name)
                else:
                    qs = qs.filter(name_simplified__contains=name)
            if album != '':
                if artist == '' and name == '':
                    qs = qs.filter(album_name_simplified=album)
                else:
                    qs = qs.filter(album_name_simplified__contains=album)

            total_count = qs.count()
            data = list(qs[offset:offset+limit].values('id', 'name', 'artist_name', 'album_name'))

        if fuzzy != '':
            data = yasearch_search.search_song(fuzzy)
            if data is not None and data != []:
                total_count = data.count()
                data = list(data[offset:offset+limit])
                for item in data:
                    item['album_name'] = item['album']
                    del item['album']
                    item['artist_name'] = item['artist']
                    del item['artist']
                    item['id'] = item['db_id']
                    del item['db_id']
                    del item['_id']

        response = api_response(data, total_count, limit=limit, offset=offset)
        return response
    elif request.method == 'POST':
        yasound_song_id = request.REQUEST.get('yasound_song_id', None)
        playlist, _created = radio.get_or_create_default_playlist()
        return add_song(request, radio_id=radio.id, playlist_index=0, yasound_song_id=yasound_song_id)

    raise Http404


@csrf_exempt
@check_api_key(methods=['GET', 'POST'], login_required=True)
def programming_status_details(request, event_id):
    pm = ProgrammingHistory()

    event = pm.find_event(event_id)
    if event and event.get('user_id') == request.user.id:
        details = pm.details_for_event(event)
        res = []
        for detail in details:
            if detail.get('status') == ProgrammingHistory.STATUS_SUCCESS:
                detail['formatted_status'] = unicode(_('success'))
            elif detail.get('status') == ProgrammingHistory.STATUS_FINISHED:
                detail['formatted_status'] = unicode(_('finished'))
            elif detail.get('status') == ProgrammingHistory.STATUS_FAILED:
                detail['formatted_status'] = unicode(_('failed'))
            elif detail.get('status') == ProgrammingHistory.STATUS_PENDING:
                detail['formatted_status'] = unicode(_('pending'))

            res.append(detail)
        response = api_response(res, len(res))
        return response
    raise Http404

@csrf_exempt
@check_api_key(methods=['GET', 'POST', 'DELETE'], login_required=True)
def my_programming_status(request, radio_uuid, event_id=None):
    radio = get_object_or_404(Radio, uuid=radio_uuid)
    if request.user != radio.creator:
        return HttpResponse(status=401)

    if request.method == 'GET':
        limit = int(request.REQUEST.get('limit', 25))
        offset = int(request.REQUEST.get('offset', 0))

        pm = ProgrammingHistory()

        events = pm.events_for_radio(radio)
        total_count = events.count()

        data = pm.events_for_radio(radio, skip=offset, limit=limit)
        res = []
        for status in data:
            if status.get('status') == ProgrammingHistory.STATUS_SUCCESS:
                status['formatted_status'] = unicode(_('success'))
            elif status.get('status') == ProgrammingHistory.STATUS_FINISHED:
                status['formatted_status'] = unicode(_('finished'))
            elif status.get('status') == ProgrammingHistory.STATUS_FAILED:
                status['formatted_status'] = unicode(_('failed'))
            elif status.get('status') == ProgrammingHistory.STATUS_PENDING:
                status['formatted_status'] = unicode(_('pending'))

            if status.get('type') == ProgrammingHistory.PTYPE_UPLOAD_PLAYLIST:
                status['formatted_type'] = unicode(_('playlist upload'))
            if status.get('type') == ProgrammingHistory.PTYPE_UPLOAD_FILE:
                status['formatted_type'] = unicode(_('file upload'))
            if status.get('type') == ProgrammingHistory.PTYPE_ADD_FROM_YASOUND:
                status['formatted_type'] = unicode(_('add from yasound'))
            if status.get('type') == ProgrammingHistory.PTYPE_ADD_FROM_DEEZER:
                status['formatted_type'] = unicode(_('add from Deezer'))
            if status.get('type') == ProgrammingHistory.PTYPE_IMPORT_FROM_ITUNES:
                status['formatted_type'] = unicode(_('import from iTunes'))
            if status.get('type') == ProgrammingHistory.PTYPE_REMOVE_FROM_PLAYLIST:
                status['formatted_type'] = unicode(_('remove from playlist'))

            res.append(status)
        response = api_response(res, total_count, limit=limit, offset=offset)
        return response
    elif request.method == 'DELETE' and event_id is not None:
        pm = ProgrammingHistory()
        event = pm.find_event(event_id)
        if event is not None:
            pm.remove_event(event)
            data = {
                'success': True,
            }
            return api_response(data)
        else:
            data = {
                'success': False,
                'message': unicode(_('Unknown event'))
            }
            return api_response(data)

    raise Http404


def get_global_minutes():
    minutes = cache.get('public.stat.minutes')
    if not minutes:
        mm = GlobalMetricsManager()
        metrics = mm.get_global_metrics()
        listening_time = 0
        for metric in metrics:
            if 'listening_time' in metric:
                listening_time += float(metric['listening_time']) / 60.0
        minutes = intcomma(int(listening_time)).replace(',', ' ')
        cache.set('public.stat.minutes', minutes, 60*5)
    return minutes

def public_stats(request):
    """
    public global stats (minutes listened on yasound)
    """
    data = {
        'minutes': get_global_minutes()
    }
    response = json.dumps(data)
    return HttpResponse(response, mimetype='application/json')

def logout(request, app_name='app'):
    next_url = reverse('webapp', args=[app_name])
    logout_url = reverse('django.contrib.auth.views.logout')
    return HttpResponseRedirect(logout_url + '?next=%s' % (next_url))

def load_template(request, template_name, app_name='app'):
    root = get_root(request, app_name)

    context = {
        'root': root,
        'app_name': app_name
    }
    if template_name == 'radio/editRadioPage.mustache':
        uuid = request.REQUEST.get('uuid', '')
        radio = get_object_or_404(Radio, uuid=uuid)
        if radio.creator != request.user:
            return HttpResponse(status=401)

        context['radio'] = radio
        context['settings_radio_form'] = SettingsRadioForm(instance=radio)
    elif template_name == 'settings/settingsPage.mustache':
        my_informations_form = MyInformationsForm(instance=request.user.get_profile())
        my_accounts_form = MyAccountsForm(instance=request.user.get_profile())
        my_notifications_form = MyNotificationsForm(user_profile=request.user.get_profile())
        display_associate_facebook = not request.user.get_profile().facebook_enabled
        display_associate_twitter = not request.user.get_profile().twitter_enabled

        context['my_informations_form'] = my_informations_form
        context['my_accounts_form'] = my_accounts_form
        context['my_notifications_form'] = my_notifications_form
        context['user_profile'] = request.user.get_profile()
        context['display_associate_facebook'] = display_associate_facebook
        context['display_associate_twitter'] = display_associate_twitter

    template_full_name = 'yabase/app/%s' % (template_name)
    return render_to_response(template_full_name, context, context_instance=RequestContext(request))


@check_api_key(methods=['GET',], login_required=False)
def user_favorites(request, username):
    """
    Simple view which returns the favorites radio for given user.
    The tastypie version only support id as user input
    """
    limit = int(request.REQUEST.get('limit', 25))
    offset = int(request.REQUEST.get('offset', 0))
    qs = Radio.objects.filter(radiouser__user__username=username, radiouser__favorite=True, deleted=False)
    total_count = qs.count()
    qs = qs[offset:offset+limit]
    data = []
    for radio in qs:
        data.append(radio.as_dict(request_user=request.user))
    response = api_response(data, total_count, limit=limit, offset=offset)
    return response

@check_api_key(methods=['GET',], login_required=False)
def user_radios(request, username):
    """
    Simple view which returns the radio owned by a given user.
    The tastypie version only support id as user input
    """
    limit = int(request.REQUEST.get('limit', 25))
    offset = int(request.REQUEST.get('offset', 0))
    qs = Radio.objects.filter(creator__username=username, deleted=False, ready=True)
    total_count = qs.count()
    qs = qs[offset:offset+limit]
    data = []
    for radio in qs:
        data.append(radio.as_dict(request_user=request.user))
    response = api_response(data, total_count, limit=limit, offset=offset)
    return response


@csrf_exempt
@check_api_key(methods=['GET', 'POST', 'DELETE'])
def my_radios(request, radio_uuid=None):
    """
    Return the owner radio with additional informations (stats)
    """
    request.user.get_profile().update_geo_restrictions(request)

    if request.method == 'GET':
        limit = int(request.REQUEST.get('limit', 25))
        offset = int(request.REQUEST.get('offset', 0))
        qs = request.user.get_profile().own_radios(only_ready_radios=False)
        total_count = qs.count()
        qs = qs[offset:offset+limit]
        data = []
        for radio in qs:
            radio_data = radio.as_dict(request_user=request.user)
            stats = RadioListeningStat.objects.daily_stats(radio, nb_days=30)
            stats_data = []
            for stat in stats:
                stats_data.append(stat.as_dict())
            radio_data['stats'] = stats_data
            data.append(radio_data)

        yabase_signals.access_my_radios.send(sender=request.user, user=request.user)

        response = api_response(data, total_count, limit=limit, offset=offset)
        return response
    elif request.method == 'POST':
        profile = request.user.get_profile()
        if not profile.permissions.create_radio:
            data = {
                'success': False,
                'message': unicode(_('You are not allowed to create a radio'))
            }
            return api_response(data)

        country = request_country(request)
        if not yageoperm_utils.can_create_radio(request.user, country):
            data = {
                'success': False,
                'message': unicode(_('This feature is not yet available for your country'))
            }
            return api_response(data)

        default_name = u'%s - %s' % ( _('new radio'), unicode(request.user.get_profile()))
        radio = Radio.objects.create(creator=request.user, name=default_name)
        radio.get_or_create_default_playlist()
        data = radio.as_dict(request_user=request.user)
        return api_response(data)
    elif request.method == 'DELETE' and radio_uuid is not None:
        radio = get_object_or_404(Radio, uuid=radio_uuid)
        if radio.creator != request.user:
            return HttpResponse(status=401)

        radio.mark_as_deleted()
        data = {
            'success': True
        }
        return api_response(data)
    raise Http404


@check_api_key(methods=['GET',], login_required=False)
def radio_leaderboard(request, radio_uuid):
    radio = get_object_or_404(Radio, uuid=radio_uuid)
    data = radio.relative_leaderboard_as_dicts()
    response = api_response(data)
    return response

@csrf_exempt
@check_api_key(methods=['GET', 'POST', 'DELETE'])
def radio_picture(request, radio_uuid, size=''):
    """
    RESTful view for handling radio picture
    """

    radio = get_object_or_404(Radio, uuid=radio_uuid)
    if request.method == 'GET':
        if size == 'xl':
            picture_url = radio.large_picture_url
        elif size == 'xs':
            picture_url = radio.small_picture_url
        elif size == '':
            picture_url = radio.picture_url
        else:
            picture_url = radio.get_picture_url(size)

        return HttpResponseRedirect(picture_url)

    if radio.creator != request.user:
        return HttpResponse(status=401)

    if request.method == 'POST':
        if not request.FILES.has_key(PICTURE_FILE_TAG):
            return HttpResponseBadRequest('Must upload a file')

        f = request.FILES[PICTURE_FILE_TAG]
        error = False

        if f.size > settings.RADIO_PICTURE_MAX_FILE_SIZE:
            error = unicode(_('The provided file is too big'))
        if f.size < settings.RADIO_PICTURE_MIN_FILE_SIZE:
            error = unicode(_('The provided file is too small'))
        if f.content_type not in settings.RADIO_PICTURE_ACCEPTED_FORMATS:
            error = unicode(_('The file format is not supported'))
        response_data = {
            "name": f.name,
            "size": f.size,
            "type": f.content_type
        }
        if error:
            response_data["error"] = error
            response_data = json.dumps([response_data])
            return HttpResponse(response_data, mimetype='application/json')

        radio.set_picture(f)

        # url for deleting the file in case user decides to delete it
        response_data["delete_url"] = reverse('yabase.views.radio_picture', kwargs={'radio_uuid':radio.uuid})
        response_data["delete_type"] = "DELETE"
        response_data["url"] = radio.picture_url

        # generate the json data
        response_data = json.dumps([response_data])
        # response type
        response_type = "application/json"

        # QUIRK HERE
        # in jQuey uploader, when it falls back to uploading using iFrames
        # the response content type has to be text/html
        # if json will be send, error will occur
        # if iframe is sending the request, it's headers are a little different compared
        # to the jQuery ajax request
        # they have different set of HTTP_ACCEPT values
        # so if the text/html is present, file was uploaded using jFrame because
        # that value is not in the set when uploaded by XHR
        if "text/html" in request.META["HTTP_ACCEPT"]:
            response_type = "text/html"

        # return the data to the uploading plugin
        return HttpResponse(response_data, mimetype=response_type)
    elif request.method == 'DELETE':
        radio.picture.delete()
        response_data = json.dumps(True)
        return HttpResponse(response_data, mimetype="application/json")
    raise Http404

@check_api_key(methods=['GET'], login_required=False)
def radio_pictures(request, radio_uuid):
    """
    return the list of pictures for displaying in the wall
    """

    radio = get_object_or_404(Radio, uuid=radio_uuid)
    response_data = json.dumps(radio.pictures)
    return HttpResponse(response_data, mimetype="application/json")

@check_api_key(methods=['GET',], login_required=False)
def listeners(request, radio_uuid):
    radio = get_object_or_404(Radio, uuid=radio_uuid)
    limit = int(request.GET.get('limit', yabase_settings.MOST_ACTIVE_RADIOS_LIMIT))
    skip = int(request.GET.get('skip', 0))

    data, total_count = radio.current_users(limit, skip)
    response = api_response(data, total_count=total_count, limit=limit, offset=skip)
    return response

@check_api_key(methods=['GET',], login_required=False)
def listeners_legacy(request, radio_id):
    radio = get_object_or_404(Radio, id=radio_id)
    limit = int(request.GET.get('limit', 10))
    skip = int(request.GET.get('skip', 0))

    # if limit == 0:
    #     limit = 100

    data, total_count = radio.current_users(limit, skip)
    response = api_response(data, total_count=total_count, limit=limit, offset=skip)
    return response


@check_api_key(methods=['GET',], login_required=False)
def fans(request, radio_uuid):
    """ Return the user who have added the radio as favorite"""

    radio = get_object_or_404(Radio, uuid=radio_uuid)
    limit = int(request.GET.get('limit', yabase_settings.MOST_ACTIVE_RADIOS_LIMIT))
    skip = int(request.GET.get('skip', 0))

    data, total_count = radio.fans(limit, skip)
    response = api_response(data, total_count=total_count, limit=limit, offset=skip)
    return response


@csrf_exempt
@check_api_key(methods=['POST',], login_required=False)
def user_watched_tutorial(request):
    yabase_signals.user_watched_tutorial.send(sender=request.user,
                                              user=request.user)
    res = {'success': True}
    return HttpResponse(json.dumps(res), mimetype='application/json')

def close(request, template_name='yabase/close.html'):
    return render_to_response(template_name, {
    }, context_instance=RequestContext(request))



def profiling(request):
    if not request.user.is_superuser:
        raise Http404
    from middleware import SqlProfilingMiddleware
    return render_to_response("yabase/profiling.html", {"queries": SqlProfilingMiddleware.Queries})


@check_api_key(methods=['POST'], login_required=False)
def generate_download_current_song_url(request, radio_uuid):
    """return a temporary token linked to user account to be given to streamer.
    """
    if not is_deezer(request):
        raise Http404

    token = uuid.uuid4().hex
    key = 'radio_%s.current_song_token.%s' % (radio_uuid, token)

    radio = get_object_or_404(Radio, uuid=radio_uuid)
    current_song = radio.current_song
    if current_song is None:
        raise Http404
    yasound_song_id = current_song.metadata.yasound_song_id
    yasound_song = YasoundSong.objects.get(id=yasound_song_id)

    cache.set(key, token, 60)
    response = {
        'url': absolute_url(reverse('download_current_song', args=[radio_uuid, token])),
        'name': yasound_song.name,
        'artist': yasound_song.artist_name,
    }
    response_data = json.dumps(response)
    return HttpResponse(response_data)


@check_api_key(methods=['GET'], login_required=False)
def download_current_song(request, radio_uuid, token):
    key = 'radio_%s.current_song_token.%s' % (radio_uuid, token)
    if cache.get(key) != token:
        raise Http404
    cache.delete(key)

    radio = get_object_or_404(Radio, uuid=radio_uuid)
    current_song = radio.current_song
    yasound_song_id = current_song.metadata.yasound_song_id
    yasound_song = YasoundSong.objects.get(id=yasound_song_id)
    path = yasound_song.get_song_lq_relative_path()

    response = HttpResponse()
    response['Content-Type'] = 'audio/mp3'
    response['X-Accel-Redirect'] = '/songs/' + path
    return response


@check_api_key(methods=['GET'], login_required=False)
def radio_m3u(request, radio_uuid, template_name='yabase/m3u.txt'):
    radio = get_object_or_404(Radio, uuid=radio_uuid)
    return render_to_response(template_name, {
        'radio': radio
    }, context_instance=RequestContext(request), mimetype='audio/x-mpegurl')
