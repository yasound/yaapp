from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.core import serializers
from django.core.urlresolvers import reverse
from django.db.models import Q, Count
from django.http import HttpResponseRedirect, HttpResponseRedirect, HttpResponse, \
    HttpResponseForbidden, Http404
from django.shortcuts import render_to_response, get_object_or_404, \
    get_list_or_404
from django.template import RequestContext
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from extjs import utils
from grids import SongInstanceGrid, RadioGrid, InvitationGrid, YasoundSongGrid
from yabackoffice.forms import RadioForm
from yabase.models import Radio, SongInstance
from yainvitation.models import Invitation
from yaref.models import YasoundSong
import simplejson as json
import utils as yabackoffice_utils


@login_required
def index(request, template_name="yabackoffice/index.html"):
    if not request.user.is_superuser:
        raise Http404()
    
    return render_to_response(template_name, {
    }, context_instance=RequestContext(request))
    
@csrf_exempt
@login_required
def radio_unmatched_song(request, radio_id):
    if not request.user.is_superuser:
        raise Http404()

    radio = get_object_or_404(Radio, id=radio_id)
    if request.method == 'GET':
        qs = radio.unmatched_songs
        grid = SongInstanceGrid()
        jsonr = yabackoffice_utils.generate_grid_rows_json(request, grid, qs)
        resp = utils.JsonResponse(jsonr)
        return resp

@csrf_exempt
@login_required
def radio_songs(request, radio_id):
    if not request.user.is_superuser:
        raise Http404()
    radio = get_object_or_404(Radio, id=radio_id)
    if request.method == 'GET':
        qs = SongInstance.objects.filter(playlist__radio=radio)

        name = request.REQUEST.get('name')
        artist_name = request.REQUEST.get('artist_name')
        album_name = request.REQUEST.get('album_name')
        
        if name:
            qs = qs.filter(metadata__name__icontains=name)
        if artist_name:
            qs = qs.filter(metadata__artist_name__icontains=artist_name)
        if album_name:
            qs = qs.filter(metadata__album_name__icontains=album_name)
            
        grid = SongInstanceGrid()
        jsonr = yabackoffice_utils.generate_grid_rows_json(request, grid, qs)
        resp = utils.JsonResponse(jsonr)
        return resp

@csrf_exempt
@login_required
def radio_remove_songs(request, radio_id):
    """
    delete song instance from radio
    """
    if not request.user.is_superuser:
        raise Http404()
    radio = get_object_or_404(Radio, id=radio_id)
    if request.method == 'POST':
        ids = request.REQUEST.getlist('song_instance_id')
        SongInstance.objects.filter(playlist__radio=radio, id__in=ids).delete()
        json_data = json.JSONEncoder(ensure_ascii=False).encode({
            'success': True,
            'message': ''
        })
        return HttpResponse(json_data, mimetype='application/json')
    raise Http404

@csrf_exempt
@login_required
def radio_add_songs(request, radio_id):
    """
    add yasound song to radio
    """
    if not request.user.is_superuser:
        raise Http404()
    radio = get_object_or_404(Radio, id=radio_id)
    if request.method == 'POST':
        ids = request.REQUEST.getlist('yasound_song_id')
        yasound_songs = YasoundSong.objects.filter(id__in=ids)
        playlist, _created = radio.get_or_create_default_playlist()
        for yasound_song in yasound_songs:
            SongInstance.objects.create_from_yasound_song(playlist, yasound_song)
        json_data = json.JSONEncoder(ensure_ascii=False).encode({
            'success': True,
            'message': ''
        })
        return HttpResponse(json_data, mimetype='application/json')
    raise Http404

@csrf_exempt
@login_required
def radios(request, radio_id=None):
    if not request.user.is_superuser:
        raise Http404()
    if request.method == 'GET':
        qs = Radio.objects.all()
        name = request.REQUEST.get('name')
        if name:
            qs = qs.filter(name__icontains=name)
        grid = RadioGrid()
        jsonr = yabackoffice_utils.generate_grid_rows_json(request, grid, qs)
        resp = utils.JsonResponse(jsonr)
        return resp
    elif request.method == 'POST':
        data = request.REQUEST.get('data')
        decoded_data = json.loads(data)
        form = RadioForm(decoded_data)
        errors = None
        success = True
        message = ''
        if form.is_valid():
            radio = form.save()
            qs = Radio.objects.filter(id=radio.id)
            grid = RadioGrid()
            jsonr = yabackoffice_utils.generate_grid_rows_json(request, grid, qs)
            resp = utils.JsonResponse(jsonr)
            return resp
        else:
            message = _("Invalid input")
            errors = form.errors
            success = False
            
            json_data = json.JSONEncoder(ensure_ascii=False).encode({
                'success': success, 
                'errors': errors,
                'message': message,
            })
            return utils.JsonResponse(json_data)
    elif request.method == 'DELETE':
        radio = get_object_or_404(Radio, id=radio_id)
        radio.empty_next_songs_queue()
        radio.delete()
        data = {"success":True,"message":"ok","data":[]}
        resp = utils.JsonResponse(json.JSONEncoder(ensure_ascii=False).encode(data))
        return resp
    raise Http404
       

@csrf_exempt
@login_required
def invitations(request):
    if not request.user.is_superuser:
        raise Http404()
    if request.method == 'GET':
        qs = Invitation.objects.all()
        grid = InvitationGrid()
        jsonr = yabackoffice_utils.generate_grid_rows_json(request, grid, qs)
        resp = utils.JsonResponse(jsonr)
        return resp
    
@csrf_exempt
@login_required
def yasound_songs(request, song_id=None):
    if not request.user.is_superuser:
        raise Http404()
    if request.method == 'GET':
        qs = YasoundSong.objects.all()
        name = request.REQUEST.get('name', '')
        artist_name = request.REQUEST.get('artist_name', '')
        album_name = request.REQUEST.get('album_name', '')

        if name:
            qs = qs.filter(name_simplified__istartswith=name)
        if artist_name:
            qs = qs.filter(artist_name_simplified__istartswith=artist_name)
        if album_name:
            qs = qs.filter(album_name_simplified__istartswith=album_name)

        grid = YasoundSongGrid()
        jsonr = yabackoffice_utils.generate_grid_rows_json(request, grid, qs)
        resp = utils.JsonResponse(jsonr)
        return resp
    raise Http404    