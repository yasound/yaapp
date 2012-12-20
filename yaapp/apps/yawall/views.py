from django.http import HttpResponseNotFound, HttpResponse, Http404
from django.shortcuts import get_object_or_404
from models import WallManager
from yacore.decorators import check_api_key
from yacore.api import api_response
from yabase.models import Radio
from yabase import signals as yabase_signals
import json


@check_api_key(methods=['GET', 'DELETE'], login_required=False)
def wall(request, radio_uuid, event_id=None):
    wm = WallManager()
    if request.method == 'GET':
        offset = int(request.REQUEST.get('offset', 0))
        try:
            limit = int(request.REQUEST.get('limit', 20))
        except:
            limit = 20
        total_count = wm.events_count_for_radio(radio_uuid)
        data = wm.events_for_radio(radio_uuid, skip=offset, limit=limit)
        return api_response(list(data), total_count=total_count, limit=limit, offset=offset)
    elif request.method == 'DELETE':
        radio = get_object_or_404(Radio, uuid=radio_uuid)
        if radio.creator != request.user:
            return HttpResponse(status=401)

        wm.remove_event(event_id)
        yabase_signals.new_moderator_del_msg_activity.send(sender=request.user, user=request.user)

        response = {'success': True}
        res = json.dumps(response)
        return HttpResponse(res)
