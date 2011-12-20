from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from yabase.models import Radio
import zlib

from yabase.task import test, process_playlists

def test_task(request):
    print 'launch task\n'
    test.delay('prout!!!')
    print 'launched task\n'
    return HttpResponse("Worked fine\n")


@csrf_exempt
def upload_playlists(request, radio_id):
    radio = get_object_or_404(Radio, pk=radio_id)

    print request.FILES
    data = request.FILES['playlists_data']
    content_compressed = data.read()
    content_uncompressed = zlib.decompress(content_compressed)
    lines = content_uncompressed.split('\n')
    
    print 'delay task process_playlists'
    process_playlists.delay(radio, lines)
    print 'delay task process_playlists 2'

    return HttpResponse("You've successfully launched playlists processing for radio '%s'\n" % radio)
