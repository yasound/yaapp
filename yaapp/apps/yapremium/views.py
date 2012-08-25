from models import Subscription
from django.shortcuts import get_object_or_404
from yacore.api import api_response
from yacore.decorators import check_api_key
from django.contrib.auth.models import User
import utils as yapremium_utils
import logging
logger = logging.getLogger("yaapp.yapremium")

@check_api_key(methods=['GET',], login_required=True)
def subscriptions(request, subscription_sku=None):
    if request.method == 'GET':
        limit = int(request.REQUEST.get('limit', 25))
        offset = int(request.REQUEST.get('offset', 0))
        qs = Subscription.objects.available_subscriptions()
        total_count = qs.count()
        qs = qs[offset:offset+limit]
        data = []
        for subscription in qs:
            data.append(subscription.as_dict(request.user))
        response = api_response(data, total_count, limit=limit, offset=offset)
        return response
    elif request.method == 'POST' and subscription_sku is not None:
        subscription = get_object_or_404(Subscription, sku=subscription_sku)
        data = json.loads(request.raw_post_data)
        username = data.get('username')
        receipt = data.get('receipt')
        validated = yapremium_utils.verifiy_receipt(receipt)
        if not validated:
            response = api_response({'success': False})
            return response
        else:
            UserSubscription.objects.create(subscription=subscription, user=request.user, active=True)
            response = api_response({'success': True})
            return response

    raise Http404
