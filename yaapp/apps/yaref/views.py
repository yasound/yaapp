from celery.result import AsyncResult
from django.http import Http404, HttpResponse, HttpResponseNotFound, \
    HttpResponseNotAllowed, HttpResponseBadRequest, HttpResponseForbidden,\
    HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from forms import SearchForm
from models import YasoundSong
from time import time
from settings import FUZZY_KEY
from django.utils import simplejson
from yacore.http import check_api_key_Authentication, check_http_method
from yaref.models import YasoundAlbum

@login_required
def find_fuzzy(request, template_name='yaref/find_fuzzy.html'):
    form = SearchForm(request.REQUEST)
    song = None
    elapsed = 0
    if form.is_valid():
        song_name = form.cleaned_data['song']
        artist_name = form.cleaned_data['artist']
        album_name = form.cleaned_data['album']
        start = time()
        song = YasoundSong.objects.find_fuzzy(song_name, album_name, artist_name)
        elapsed = time() - start

    return render_to_response(template_name, {
        "song": song,
        "elapsed": elapsed,
        "form": form,
    }, context_instance=RequestContext(request))    
    
@csrf_exempt
def find_fuzzy_json(request):
    decoded = simplejson.loads(request.raw_post_data)
    name = decoded['name']
    album = decoded['album']
    artist = decoded['artist']
    key = decoded['key']
    if key != FUZZY_KEY:
        return HttpResponseForbidden()
    
    song = YasoundSong.objects.find_fuzzy(name, album, artist)
    if song:
        db_id = song['db_id']
    else:
        db_id = None
    to_json = {
        "db_id": db_id,
    }
    return HttpResponse(simplejson.dumps(to_json), mimetype='application/json')

def album_cover(request, album_id):
    if not check_api_key_Authentication(request):
        return HttpResponse(status=401)
    if not check_http_method(request, ['get']):
        return HttpResponse(status=405)
    
    album = get_object_or_404(YasoundAlbum, id=album_id)
    url = album.cover_url
    if not url:
        url = '/media/images/default_image.png'
    return HttpResponseRedirect(url)

