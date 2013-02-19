from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from yacore.decorators import check_api_key
from yacore.api import api_response
from yabase.models import Radio
from models import JingleManager
from django.views.decorators.csrf import csrf_exempt
import json
from tempfile import mkdtemp
from django.conf import settings
from shutil import rmtree
from task import import_jingle
import os


@check_api_key(methods=['GET'], login_required=True)
def jingles(request, radio_uuid):
    """Return available jingles for radio. """
    radio = get_object_or_404(Radio, uuid=radio_uuid)
    if radio.creator != request.user:
        return HttpResponse(status=401)

    jm = JingleManager()
    jingles = jm.jingles_for_radio(radio_uuid)
    data = [jingle for jingle in jingles]
    response = api_response(data)
    return response


@csrf_exempt
@check_api_key(methods=['POST'], login_required=True)
def upload(request, song_id=None):
    """
    Upload a jingle

    A metadata json dict must be provided::
        dict = {
            'radio_uuid': radio_uuid,
            'name': 'jingle name'
        }

    """
    f = request.FILES.get('jingle')
    if f is None:
        return HttpResponse('request does not contain a song file')

    json_data = {}
    data = request.REQUEST.get('data')
    if data:
        json_data = json.loads(data)
    else:
        return HttpResponse('request does not contain metadata')

    radio_uuid = json_data.get('radio_uuid')
    radio = get_object_or_404(Radio, uuid=radio_uuid)
    if radio.creator != request.user:
        return HttpResponse(status=401)

    name = json_data.get('name', 'no name')

    directory = mkdtemp(dir=settings.SHARED_TEMP_DIRECTORY)
    _path, extension = os.path.splitext(f.name)
    source = u'%s/s%s' % (directory, extension)
    source_f = open(source, 'wb')
    for chunk in f.chunks():
        source_f.write(chunk)
    source_f.close()

    import_jingle(filename=source, name=name, radio_uuid=radio_uuid, creator_id=request.user.id)
    rmtree(directory)

    response_format = request.REQUEST.get('response_format', '')
    if response_format == 'json':
        response_data = {
            "name": f.name,
            "size": f.size,
            "type": f.content_type
        }
        response_data = json.dumps([response_data])
        response_type = "application/json"
        if "text/html" in request.META["HTTP_ACCEPT"]:
            response_type = "text/html"
        return HttpResponse(response_data, mimetype=response_type)
    else:
        res = 'upload OK for jingle: %s' % unicode(f.name)
    return HttpResponse(res)


@csrf_exempt
@check_api_key(methods=['POST', 'PUT', 'DELETE'], login_required=True)
def jingle(request, id):
    """RESTful view for jingle """
    jm = JingleManager()
    jingle = jm.jingle(id)
    if jingle is None:
        raise Http404
    if jingle.get('creator') != request.user.id:
        return HttpResponse(status=401)
    if request.method == 'PUT':
        payload = json.loads(request.raw_post_data)
        name = payload.get('name')
        jingle['name'] = name
        jm.update_jingle(jingle)
        return api_response(jingle)
    elif request.method == 'DELETE':
        jm.delete_jingle(id)
        return api_response({'success': True})
