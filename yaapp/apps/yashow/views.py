from django.http import HttpResponseNotFound, HttpResponse
from models import ShowManager
from yacore.decorators import check_api_key
from yacore.api import MongoAwareEncoder, api_response
import json
from yabase.models import Playlist, Radio, SongInstance
from django.shortcuts import get_object_or_404
import datetime
from django.views.decorators.csrf import csrf_exempt
import logging

logger = logging.getLogger("yaapp.yabase")

@check_api_key(methods=['GET'], login_required=True)
def get_shows_for_radio(request, radio_uuid):
    radio = get_object_or_404(Radio, uuid=radio_uuid)
    if radio.creator != request.user:
        return HttpResponseNotFound()
    
    offset = int(request.REQUEST.get('offset', 0))
    limit = request.REQUEST.get('limit', None)
    if limit is not None:
        limit = int(limit)
        
    m = ShowManager()
    shows = list(m.shows_for_radio(radio.id, count=limit, skip=offset))
    
    res = api_response(shows, limit=limit, offset=offset)
    return res

@check_api_key(methods=['GET', 'DELETE', 'PUT'], login_required=True)
def show(request, show_id):
    m = ShowManager()
    s = m.get_show(show_id)
    
    if s is None:
        return HttpResponseNotFound()
    creator = Playlist.objects.get(id=s['playlist_id']).radio.creator
    if creator != request.user:
        return HttpResponseNotFound()
    
    if request.method == 'GET':
        res = json.dumps(s, cls=MongoAwareEncoder)
        return HttpResponse(res)
    
    elif request.method == 'DELETE':
        m.delete_show(show_id)
        response = {'success': True}
        res = json.dumps(response)
        return HttpResponse(res)
    
    elif request.method == 'PUT':
        data = json.loads(request.raw_post_data)
        if not data.has_key('playlist_id'):
            return HttpResponseNotFound()
        playlist_id = data['playlist_id']
        playlist = get_object_or_404(Playlist, id=playlist_id)
        if playlist.radio.creator != request.user:
            return HttpResponseNotFound()
        s=  m.update_show(data)
        res = json.dumps(s, cls=MongoAwareEncoder)
        return HttpResponse(res)

    else:
        return HttpResponseNotFound()
    
@csrf_exempt
@check_api_key(methods=['POST'], login_required=True)
def create_show(request, radio_uuid):
    radio = get_object_or_404(Radio, uuid=radio_uuid)
    if radio.creator != request.user:
        logger.info('request user is not the creator of the radio: do not have rights to create a show')
        return HttpResponseNotFound()
    
    m = ShowManager()
    
    data = request.POST.keys()[0]
    post_data_dict = json.loads(data)
    n = post_data_dict.get('name', '')
    d = post_data_dict.get('days', '')
    t = post_data_dict.get('time', datetime.time(hour=20, minute=0))
    random = post_data_dict.get('random_play', True)
    yasound_song_ids = post_data_dict.get('song_ids', [])
        
    show = m.create_show(name=n, radio=radio, days=d, time=t, random_play=random, yasound_songs=yasound_song_ids)

    res = json.dumps(show, cls=MongoAwareEncoder)
    return HttpResponse(res)

@check_api_key(methods=['GET'], login_required=True)
def duplicate_show(request, show_id):
    m = ShowManager()
    s = m.get_show(show_id)
    
    if s is None:
        return HttpResponseNotFound()
    creator = Playlist.objects.get(id=s['playlist_id']).radio.creator
    if creator != request.user:
        return HttpResponseNotFound()
    
    show_copy = m.duplicate_show(show_id)
    res = json.dumps(show_copy, cls=MongoAwareEncoder)
    return HttpResponse(res)

@check_api_key(methods=['GET'], login_required=True)
def get_songs_for_show(request, show_id):
    m = ShowManager()
    show = m.get_show(show_id)
    if show is None:
        return HttpResponseNotFound()
    playlist = get_object_or_404(Playlist, id=show['playlist_id'])
    if playlist.radio.creator != request.user:
        return HttpResponseNotFound()
    
    offset = int(request.REQUEST.get('offset', 0))
    limit = request.REQUEST.get('limit', None)
    if limit is not None:
        limit = int(limit)
    songs = m.songs_for_show(show_id, skip=offset, count=limit)
    song_data = []
    for s in songs:
        song_data.append(s.song_description())
    res = api_response(song_data, limit=limit, offset=offset)
    return res

@check_api_key(methods=['GET'], login_required=True)
def add_song_in_show(request, show_id, yasound_song_id):
    m = ShowManager()
    show = m.get_show(show_id)
    if show is None:
        return HttpResponseNotFound()
    playlist = get_object_or_404(Playlist, id=show['playlist_id'])
    if playlist.radio.creator != request.user:
        return HttpResponseNotFound()

    m.add_song_in_show(show_id, yasound_song_id)
    
    response = {'success':True}
    return HttpResponse(json.dumps(response))

@check_api_key(methods=['GET'], login_required=True)
def remove_song_from_show(request, show_id, song_instance_id):
    m = ShowManager()
    show = m.get_show(show_id)
    if show is None:
        return HttpResponseNotFound()
    playlist = get_object_or_404(Playlist, id=show['playlist_id'])
    if playlist.radio.creator != request.user:
        return HttpResponseNotFound()
    
    _song_instance = get_object_or_404(SongInstance, id=song_instance_id)
    
    m.remove_song(song_instance_id)
    
    response = {'success':True}
    return HttpResponse(json.dumps(response))
    