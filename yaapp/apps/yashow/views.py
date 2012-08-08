from django.http import HttpResponseNotFound, HttpResponse
from models import ShowManager
from yacore.decorators import check_api_key
from yacore.api import MongoAwareEncoder, api_response
import json
from yabase.models import Playlist, Radio
from django.shortcuts import get_object_or_404
import datetime

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
        if len(request.POST.keys()) > 1: # for the tests in yashow.test.py
            data = {}
            for k in request.POST:
                data[k] = request.POST.get(k)
        else:
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
    
@check_api_key(methods=['POST'], login_required=True)
def create_show(request, radio_uuid):
    radio = get_object_or_404(Radio, uuid=radio_uuid)
    
    m = ShowManager()
    
    data = request.POST.keys()[0]
    post_data_dict = json.loads(data)
    n = post_data_dict.get('name', '')
    d = post_data_dict.get('day', m.EVERY_DAY)
    t = post_data_dict.get('time', datetime.time(hour=20, minute=0))
    random = post_data_dict.get('random_play', True)
   
    show = m.create_show(name=n, radio=radio, day=d, time=t, random_play=random)

    res = json.dumps(show, cls=MongoAwareEncoder)
    return HttpResponse(res)

    