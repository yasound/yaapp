from models import Subscription, UserSubscription
from django.shortcuts import get_object_or_404
from yacore.api import api_response
from yacore.decorators import check_api_key
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.http import Http404, HttpResponse, HttpResponseNotFound, \
    HttpResponseBadRequest, HttpResponseRedirect
import utils as yapremium_utils
import logging
logger = logging.getLogger("yaapp.yapremium")

@csrf_exempt
@check_api_key(methods=['GET', 'POST'])
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
        logger.debug('received receipt')
        logger.debug(request)

        subscription = get_object_or_404(Subscription, sku=subscription_sku)
        receipt = request.REQUEST.get('receipt')
        username = request.REQUEST.get('username')
        if username != request.user.username:
            return HttpResponse(status=403)
        validated = yapremium_utils.verifiy_receipt(receipt)
        if not validated:
            logger.debug('receipt is invalid')
            response = api_response({'success': False})
            return response
        else:
            logger.debug('receipt is valid, creating user subscription')
            UserSubscription.objects.create(subscription=subscription, user=request.user, active=True)
            response = api_response({'success': True})
            return response

    raise Http404
