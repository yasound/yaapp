from models import FriendActivityManager, RadioActivityManager
from yacore.decorators import check_api_key
from yacore.api import api_response


@check_api_key(methods=['GET'])
def friends_activity(request):
    """ return friends activity for current user """

    fa = FriendActivityManager()
    offset = int(request.REQUEST.get('offset', 0))
    try:
        limit = int(request.REQUEST.get('limit', 20))
    except:
        limit = 20
    total_count = fa.activities_for_user(user=request.user, skip=offset, limit=limit).count()
    data = fa.activities_for_user(user=request.user, skip=offset, limit=limit)
    return api_response(list(data), total_count=total_count, limit=limit, offset=offset)


@check_api_key(methods=['GET'])
def radios_activity(request):
    """ return radios activity for current user """

    m = RadioActivityManager()
    offset = int(request.REQUEST.get('offset', 0))
    try:
        limit = int(request.REQUEST.get('limit', 20))
    except:
        limit = 20
    total_count = m.activities_for_user(user=request.user, skip=offset, limit=limit).count()
    data = m.activities_for_user(user=request.user, skip=offset, limit=limit)
    return api_response(list(data), total_count=total_count, limit=limit, offset=offset)
