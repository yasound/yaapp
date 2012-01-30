from celery.result import AsyncResult
from django.http import Http404, HttpResponse, HttpResponseNotFound, \
    HttpResponseNotAllowed, HttpResponseBadRequest
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from forms import SearchForm
from models import YasoundSong

@login_required
def find_fuzzy(request, template_name='yaref/find_fuzzy.html'):
    form = SearchForm(request.REQUEST)
    song = None
    if form.is_valid():
        song_name = form.cleaned_data['song']
        artist_name = form.cleaned_data['artist']
        album_name = form.cleaned_data['album']
        
        song = YasoundSong.objects.find_fuzzy(song_name, album_name, artist_name)

    return render_to_response(template_name, {
        "song": song,
        "form": form,
    }, context_instance=RequestContext(request))    
    
    
