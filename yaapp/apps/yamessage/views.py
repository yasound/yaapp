from django.http import HttpResponseNotFound, HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from models import NotificationsManager
from yacore.decorators import check_api_key
from yacore.api import MongoAwareEncoder, api_response
import signals as yamessage_signals
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

    total_count = m.notifications_for_recipient(request.user.id, read_status=read_status).count()

    notif_cursor = m.notifications_for_recipient(request.user.id,
                                                 count=limit,
                                                 skip=offset,
                                                 date_greater_than=date_greater_than,
                                                 date_lower_than=date_lower_than,
                                                 read_status=read_status)
    notifs = list(notif_cursor)

    yamessage_signals.access_notifications.send(sender=request.user, user=request.user)

    return api_response(notifs, total_count=total_count, limit=limit, offset=offset)


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
    data = json.loads(request.raw_post_data)
    m = NotificationsManager()

    if 'dest_user_id' not in data or int(data['dest_user_id']) != request.user.id:
        raise Http404

    n = m.update_notification(data)
    res = json.dumps(n, cls=MongoAwareEncoder)
    return HttpResponse(res)


@check_api_key(methods=['DELETE'])
def delete_notification(request, notif_id):
    m = NotificationsManager()
    n = m.get_notification(notif_id)
    if n is None:
        raise Http404

    if 'dest_user_id' not in n or int(n['dest_user_id']) != request.user.id:
        raise Http404

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


@csrf_exempt
@check_api_key(methods=['POST'])
def mark_all_as_read(request):
    m = NotificationsManager()
    m.mark_all_as_read(request.user.id)
    response = {'succeeded': True}
    res = json.dumps(response)
    return HttpResponse(res)


@check_api_key(methods=['GET'])
def unread_count(request):
    m = NotificationsManager()
    unread_count = m.unread_count(request.user.id)
    response = {'unread_count': unread_count}
    res = json.dumps(response)
    return HttpResponse(res)
