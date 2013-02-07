from celery.result import AsyncResult
from django.http import Http404, HttpResponse, HttpResponseNotFound, \
    HttpResponseNotAllowed, HttpResponseBadRequest, HttpResponseForbidden,\
    HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.conf import settings
from forms import SearchForm
from models import YasoundSong
from time import time
from settings import FUZZY_KEY
from django.utils import simplejson
from yacore.http import check_api_key_Authentication, check_http_method
from yacore.decorators import check_api_key
from yaref.models import YasoundAlbum
import logging
logger = logging.getLogger("yaapp.yaref")

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
    url = album.large_cover_url
    if not url:
        url = '/media/images/default_image.png'
    return HttpResponseRedirect(url)

@csrf_exempt
@check_api_key(methods=['POST'], login_required=False)
def internal_songs(request):
    key = request.REQUEST.get('key')
    if key != settings.DOWNLOAD_KEY:
        raise Http404
    limit = int(request.POST.get('limit', 25))
    skip = int(request.POST.get('skip', 0))

    qs = YasoundSong.objects.all().order_by('id')[skip:skip + limit]
    data = []
    for song in qs:
        data.append(song.as_dict())
    return HttpResponse(simplejson.dumps(data), mimetype='application/json')


@csrf_exempt
@check_api_key(methods=['POST'], login_required=False)
def internal_song_download(request, song_id):
    logger.debug('received internal_song_download for song %s' % (song_id))
    key = request.REQUEST.get('key')
    if key != settings.DOWNLOAD_KEY:
        logger.debug('key invalid: %s' % (key))
        raise Http404

    yasound_song = YasoundSong.objects.get(id=song_id)
    path = yasound_song.get_song_lq_relative_path()

    response = HttpResponse()
    response['Content-Type'] = 'audio/mp3'
    response['X-Accel-Redirect'] = '/songs/' + path
    return response
