from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from yabase.models import Radio
import zlib
from celery.result import AsyncResult

from yabase.task import test, process_playlists

def test_task(request):
    print 'launch task\n'
    res = test.delay('prout!!!')
    
    return HttpResponse(res.task_id)

def task_status(request, task_id):
    asyncRes = AsyncResult(task_id=task_id)
    status = asyncRes.state
    return HttpResponse(status)


@csrf_exempt
def upload_playlists(request, radio_id):
    radio = get_object_or_404(Radio, pk=radio_id)

    print request.FILES
    data = request.FILES['playlists_data']
    content_compressed = data.read()
    content_uncompressed = zlib.decompress(content_compressed)
    lines = content_uncompressed.split('\n')
    
    asyncRes = process_playlists.delay(radio, lines)

    return HttpResponse(asyncRes.task_id)
