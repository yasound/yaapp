from django.http import HttpResponseNotFound, HttpResponse, Http404
from models import WallManager
from yacore.decorators import check_api_key
from yacore.api import api_response
import json


@check_api_key(methods=['GET'], login_required=False)
def wall(request, radio_uuid):
    wm = WallManager()
    offset = int(request.REQUEST.get('offset', 0))
    limit = request.REQUEST.get('limit', 20)
    total_count = wm.events_count_for_radio(radio_uuid)
    data = wm.events_for_radio(radio_uuid, skip=offset, limit=limit)
    return api_response(list(data), total_count=total_count, limit=limit, offset=offset)
