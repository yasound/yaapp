from django.http import Http404
from yacore.api import api_response
from models import RadiosManager
from yabase.models import Radio


def search_songs_in_radios(request):
    query = request.REQUEST.get('q', '')
    limit = int(request.REQUEST.get('limit', 25))
    skip = int(request.GET.get('skip', 0))

    rm = RadiosManager()
    res = rm.search(query, limit=limit)
    total_count = len(res)
    data = []
    for r in res:
        data.append(r.as_dict(request.user))
    response = api_response(data[skip:limit + skip], total_count=total_count, limit=limit, offset=skip)
    return response


def search_radios(request):
    query = request.REQUEST.get('q', '')
    limit = int(request.REQUEST.get('limit', 25))
    skip = int(request.GET.get('skip', 0))

    rm = RadiosManager()
    res = rm.search(query, limit=limit)
    total_count = len(res)
    data = []
    for r in res:
        data.append(r.as_dict(request.user))
    response = api_response(data[skip:limit + skip], total_count=total_count, limit=limit, offset=skip)
    return response
