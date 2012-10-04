from models import Subscription, UserSubscription, UserService, Gift, Promocode
from django.shortcuts import get_object_or_404
from yacore.api import api_response
from yacore.decorators import check_api_key
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.http import Http404, HttpResponse
import utils as yapremium_utils
import logging
from transmeta import get_real_fieldname
from task import async_win_gift
import settings as yapremium_settings
import json

logger = logging.getLogger("yaapp.yapremium")


@csrf_exempt
@check_api_key(methods=['GET', 'POST'])
def subscriptions(request, subscription_sku=None):
    if request.method == 'GET':
        limit = int(request.REQUEST.get('limit', 25))
        offset = int(request.REQUEST.get('offset', 0))
        qs = Subscription.objects.available_subscriptions()
        total_count = qs.count()
        qs = qs[offset:offset +limit]
        data = []
        for subscription in qs:
            data.append(subscription.as_dict(request.user))
        response = api_response(data, total_count, limit=limit, offset=offset)
        return response
    elif request.method == 'POST' and subscription_sku is not None:
        sku_fieldname = get_real_fieldname('sku')
        kwargs = {
            '{0}__{1}'.format(sku_fieldname, 'exact'): subscription_sku,
        }
        subscription = get_object_or_404(Subscription, **kwargs)
        receipt = request.REQUEST.get('receipt')
        username = request.REQUEST.get('username')
        if username != request.user.username:
            return HttpResponse(status=403)
        validated = yapremium_utils.verify_receipt(receipt, encode=False)
        if not validated:
            logger.debug('receipt is invalid')
            response = api_response({'success': False})
            return response
        else:
            logger.debug('receipt is valid, creating user subscription')
            UserSubscription.objects.create(subscription=subscription, user=request.user)
            response = api_response({'success': True})
            return response

    raise Http404


@csrf_exempt
@check_api_key(methods=['GET', 'POST'])
def services(request, subscription_sku=None):
    if request.method == 'GET':
        limit = int(request.REQUEST.get('limit', 25))
        offset = int(request.REQUEST.get('offset', 0))
        qs = UserService.objects.filter(user=request.user)
        total_count = qs.count()
        qs = qs[offset:offset +limit]
        data = []
        for us in qs:
            data.append(us.as_dict())
        response = api_response(data, total_count, limit=limit, offset=offset)
        return response
    raise Http404


@csrf_exempt
@check_api_key(methods=['GET'], login_required=False)
def gifts(request, subscription_sku=None):
    if request.method == 'GET':
        limit = int(request.REQUEST.get('limit', 25))
        offset = int(request.REQUEST.get('offset', 0))

        qs = Gift.objects.filter(enabled=True)
        if request.user.is_anonymous():
            qs = qs.filter(authentication_needed=False)
        else:
            qs = qs.filter(authentication_needed=True)
        total_count = qs.count()
        qs = qs[offset:offset +limit]
        data = []
        for gift in qs:
            data.append(gift.as_dict(request.user))
        response = api_response(data, total_count, limit=limit, offset=offset)
        return response
    raise Http404


@csrf_exempt
@check_api_key(methods=['POST'])
def action_watch_tutorial_completed(request, username):
    user = get_object_or_404(User, username=username)
    if request.user.username != user.username:
        return HttpResponse(status=401)
    async_win_gift.delay(user_id=user.id, action=yapremium_settings.ACTION_WATCH_TUTORIAL)

@csrf_exempt
@check_api_key(methods=['POST'])
def activate_promocode(request):
    code = request.REQUEST.get('code')
    up = Promocode.objects.create_from_code(code=code, user=request.user)
    success = False
    if up:
        success = True
    res = {'success': success}
    response = json.dumps(res)
    return HttpResponse(response)
