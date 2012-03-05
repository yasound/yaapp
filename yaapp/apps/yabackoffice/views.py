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
from grids import SongInstanceGrid, RadioGrid, InvitationGrid
from yabase.models import Radio, SongInstance
from yainvitation.models import Invitation
import simplejson as json
import utils as yabackoffice_utils



@login_required
def index(request, template_name="yabackoffice/index.html"):
    return render_to_response(template_name, {
    }, context_instance=RequestContext(request))
    
@csrf_exempt
@login_required
def radio_unmatched_song(request, radio_id):
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
    radio = get_object_or_404(Radio, id=radio_id)
    if request.method == 'GET':
        qs = SongInstance.objects.filter(playlist__radio=radio)
        grid = SongInstanceGrid()
        jsonr = yabackoffice_utils.generate_grid_rows_json(request, grid, qs)
        resp = utils.JsonResponse(jsonr)
        return resp

@csrf_exempt
@login_required
def radio_remove_songs(request, radio_id):
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
def radios(request):
    if request.method == 'GET':
        qs = Radio.objects.all()
        grid = RadioGrid()
        jsonr = yabackoffice_utils.generate_grid_rows_json(request, grid, qs)
        resp = utils.JsonResponse(jsonr)
        return resp

@csrf_exempt
@login_required
def invitations(request):
    if request.method == 'GET':
        qs = Invitation.objects.all()
        grid = InvitationGrid()
        jsonr = yabackoffice_utils.generate_grid_rows_json(request, grid, qs)
        resp = utils.JsonResponse(jsonr)
        return resp