from models import Subscription
from yacore.api import api_response
from yacore.decorators import check_api_key
import logging
logger = logging.getLogger("yaapp.yapremium")

@check_api_key(methods=['GET',], login_required=False)
def subscriptions(request):
    limit = int(request.REQUEST.get('limit', 25))
    offset = int(request.REQUEST.get('offset', 0))
    qs = Subscription.objects.available_subscriptions()
    total_count = qs.count()
    qs = qs[offset:offset+limit]
    data = []
    for subscription in qs:
        data.append(subscription.as_dict())
    response = api_response(data, total_count, limit=limit, offset=offset)
    return response

