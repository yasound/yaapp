from django.http import HttpResponseNotFound, HttpResponse
from models import NotificationsManager
from yacore.decorators import check_api_key
from yacore.api import MongoAwareEncoder, api_response
import json

@check_api_key(methods=['GET'])
def get_notifications(request):
    m = NotificationsManager()
    date_greater_than = request.REQUEST.get('date__gt', None)
    date_lower_than = request.REQUEST.get('date__lt', None)
    
    offset = int(request.REQUEST.get('offset', 0))
    limit = request.REQUEST.get('limit', None)
    read_status = request.REQUEST.get('read_status', 'all')
    
    if limit is not None:
        limit = int(limit)
    
    notif_cursor = m.notifications_for_recipient(request.user.id, 
                                                 count=limit, 
                                                 skip=offset, 
                                                 date_greater_than=date_greater_than, 
                                                 date_lower_than=date_lower_than,
                                                 read_status=read_status)
    notifs = list(notif_cursor)
    return api_response(notifs, limit=limit, offset=offset)

@check_api_key(methods=['GET'])
def get_notification(request, notif_id):
    m = NotificationsManager()
    n = m.get_notification(notif_id)
    if n is None or n['dest_user_id'] != request.user.id:
        return HttpResponseNotFound()
    res = json.dumps(n, cls=MongoAwareEncoder)
    return HttpResponse(res)

@check_api_key(methods=['PUT'])
def update_notification(request, notif_id):
    if len(request.POST.keys()) > 1: # for the tests in yamessage.test.py
        data = {}
        for k in request.POST:
            data[k] = request.POST.get(k)
    else:
        data = json.loads(request.raw_post_data)
    m = NotificationsManager()
    if not data.has_key('dest_user_id') or int(data['dest_user_id']) != request.user.id:
        return HttpResponseNotFound()
    n = m.update_notification(data)
    res = json.dumps(n, cls=MongoAwareEncoder)
    return HttpResponse(res)


@check_api_key(methods=['DELETE'])
def delete_notification(request, notif_id):
    m = NotificationsManager()
    n = m.get_notification(notif_id)
    if not n.has_key('dest_user_id') or int(n['dest_user_id']) != request.user.id:
        return HttpResponseNotFound()
    
    m.delete_notification(notif_id)
    response = {'succeeded': True}
    res = json.dumps(response)
    return HttpResponse(res)

@check_api_key(methods=['DELETE'])
def delete_all_notifications(request):
    m = NotificationsManager()
    m.delete_all_notifications(request.user.id)
    response = {'succeeded': True}
    res = json.dumps(response)
    return HttpResponse(res)
