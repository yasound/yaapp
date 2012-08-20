from bson import objectid
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse
import datetime
from django.utils import simplejson

class MongoAwareEncoder(DjangoJSONEncoder):
    """JSON encoder class that adds support for Mongo objectids."""
    def default(self, o):
        if isinstance(o, objectid.ObjectId):
            return str(o)
        elif type(o) == datetime.datetime:
            return o.isoformat()
        else:
            return super(MongoAwareEncoder, self).default(o)

def api_response(data, total_count=None, limit=None, offset=0, next_url=None, previous_url=None):
    """
    return standardized response with the following example scheme :

    {"meta": {"previous": null, "total_count": 2, "offset": 2, "limit": 2, "next": null}, "objects": []}

    """
    if type(data) == type([]):
        if total_count is None:
            total_count = len(data)
        if limit is None:
            limit = total_count

        response = {
            'meta':{
                'limit': limit,
                'next': next_url,
                'offset': offset,
                'previous': previous_url,
                'total_count': total_count
            },
            'objects': data
        }
        json_response = simplejson.dumps(response, cls=MongoAwareEncoder)
        return HttpResponse(json_response, mimetype='application/json')
    else:
        json_response = simplejson.dumps(data, cls=MongoAwareEncoder)
        return HttpResponse(json_response, mimetype='application/json')

def api_response_raw(data):
    json_response = simplejson.dumps(data, cls=MongoAwareEncoder)
    return HttpResponse(json_response, mimetype='application/json')
