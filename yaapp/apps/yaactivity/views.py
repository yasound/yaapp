from django.http import HttpResponseNotFound, HttpResponse, Http404
from models import FriendActivityManager
from yacore.decorators import check_api_key
from yacore.api import api_response
import json


@check_api_key(methods=['GET'])
def friends_activity(request):
    fa = FriendActivityManager()
    offset = int(request.REQUEST.get('offset', 0))
    try:
        limit = int(request.REQUEST.get('limit', 20))
    except:
        limit = 20
    total_count = fa.activities_for_user(user=request.user, skip=offset, limit=limit).count()
    data = fa.activities_for_user(user=request.user, skip=offset, limit=limit)
    return api_response(list(data), total_count=total_count, limit=limit, offset=offset)
