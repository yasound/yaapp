from bson import objectid
from django.core.serializers.json import DjangoJSONEncoder
import datetime

class MongoAwareEncoder(DjangoJSONEncoder):
    """JSON encoder class that adds support for Mongo objectids."""
    def default(self, o):
        if isinstance(o, objectid.ObjectId):
            return str(o)
        elif type(o) == datetime.datetime:
            return o.isoformat()
        else:
            return super(MongoAwareEncoder, self).default(o)