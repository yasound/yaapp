from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from yabase.models import Radio
import zlib
from celery.result import AsyncResult
import datetime

from yabase.task import process_playlists

PICTURE_FILE_TAG = 'picture'

def task_status(request, task_id):
    asyncRes = AsyncResult(task_id=task_id)
    status = asyncRes.state
    return HttpResponse(status)


@csrf_exempt
def upload_playlists(request, radio_id):
    radio = get_object_or_404(Radio, pk=radio_id)

    print 'upload_playlists'
    print radio
    print request.FILES
    data = request.FILES['playlists_data']
    content_compressed = data.read()
    content_uncompressed = zlib.decompress(content_compressed)
    lines = content_uncompressed.split('\n')
    
    asyncRes = process_playlists.delay(radio, lines)

    return HttpResponse(asyncRes.task_id)

@csrf_exempt
def set_radio_picture(request, radio_id):
    print 'set_radio_picture'
    try:
        radio = Radio.objects.get(id=radio_id)
    except Radio.DoesNotExist:
        return HttpResponse('radio does not exist')
    
    if not request.FILES.has_key(PICTURE_FILE_TAG):
        return HttpResponse('request does not contain a picture file')
    
    f = request.FILES[PICTURE_FILE_TAG]
    d = datetime.datetime.now()
    filename = unicode(d) + '.png'
    
    radio.picture.save(filename, f, save=True)
    
    res = 'picture OK for radio: %s' % unicode(radio)
    return HttpResponse(res)
