from django.http import Http404
from yacore.api import api_response

def search(request):
    query = request.REQUEST.get('q', '')
    limit = int(request.REQUEST.get('limit', 25))
    skip = int(request.GET.get('skip', 0))
    raise Http404
