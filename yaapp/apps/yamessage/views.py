from models import NotificationsManager
from yacore.decorators import check_api_key
from django.http import HttpResponseNotFound, HttpResponse
from yacore.json import MongoAwareEncoder
import json

@check_api_key(methods=['GET'])
def get_notifications(request):
    m = NotificationsManager()
    date_greater_than = request.GET.get('date__gt', None)
    date_lower_than = request.GET.get('date__lt', None)
    skip = request.GET.get('skip', 0)
    limit = request.GET.get('limit', None)
    notif_cursor = m.notifications_for_recipient(request.user.id, count=limit, skip=skip, date_greater_than=date_greater_than, date_lower_than=date_lower_than)
    notifs = list(notif_cursor)
#    encoder = YasounJsonEncoder()
#    res = encoder.encode(notifs)
    res = json.dumps(notifs, cls=MongoAwareEncoder)
    return HttpResponse(res)

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
    print 'update_notification view'
    if len(request.POST.keys()) > 1: 
        data = request.POST # for the tests in yamessage.test.py
    else:
        data = json.loads(request.POST.keys()[0]) # strange stuff !!! but it works with requests from ios
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
