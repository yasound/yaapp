from models import Subscription, UserSubscription, UserService, Gift, Promocode
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import get_object_or_404
from yacore.api import api_response
from yacore.decorators import check_api_key
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.http import Http404, HttpResponse, HttpResponseRedirect
import utils as yapremium_utils
import logging
from transmeta import get_real_fieldname
from task import async_win_gift, async_check_follow_yasound_on_twitter, async_check_like_yasound_on_facebook
import settings as yapremium_settings
import json
import tweepy
from django.conf import settings

logger = logging.getLogger("yaapp.yapremium")


@csrf_exempt
@check_api_key(methods=['GET', 'POST'])
def subscriptions(request, subscription_sku=None):
    if request.method == 'GET':
        limit = int(request.REQUEST.get('limit', 25))
        offset = int(request.REQUEST.get('offset', 0))
        qs = Subscription.objects.available_subscriptions()
        total_count = qs.count()
        qs = qs[offset:offset + limit]
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
        qs = qs[offset:offset + limit]
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
        qs = Gift.objects.filter(enabled=True)
        if request.user.is_anonymous():
            qs = qs.filter(authentication_needed=False)
        else:
            qs = qs.filter(authentication_needed=True)
        data = []
        for gift in qs:
            gift_dict = gift.as_dict(request.user)
            if gift_dict.get('enabled'):
                data.append(gift_dict)

        response = api_response(data, len(data))
        return response
    raise Http404


@csrf_exempt
@check_api_key(methods=['POST'])
def action_watch_tutorial_completed(request):
    async_win_gift.delay(user_id=user.id, action=yapremium_settings.ACTION_WATCH_TUTORIAL)
    res = {'success': True}
    response = json.dumps(res)
    return HttpResponse(response)


@csrf_exempt
@check_api_key(methods=['POST'])
def action_follow_yasound_on_twitter_completed(request):
    profile = request.user.get_profile()
    if not profile.twitter_enabled:
        res = {'success': False, 'message': unicode(_('your account is not associated with twitter.'))}
        response = json.dumps(res)
        return HttpResponse(response)

    auth = tweepy.OAuthHandler(settings.YASOUND_TWITTER_APP_CONSUMER_KEY, settings.YASOUND_TWITTER_APP_CONSUMER_SECRET)
    auth.set_access_token(profile.twitter_token, profile.twitter_token_secret)
    api = tweepy.API(auth)
    api.create_friendship(screen_name='YasoundSAS')
    async_check_follow_yasound_on_twitter.apply_async(args=[request.user.id])

    res = {'success': True, 'message': unicode(_('Thank you, your gift will be available soon.'))}
    response = json.dumps(res)
    return HttpResponse(response)

@csrf_exempt
@check_api_key(methods=['POST'])
def action_like_yasound_on_facebook_completed(request):
    profile = request.user.get_profile()
    if not profile.facebook_enabled:
        res = {'success': False, 'message': unicode(_('your account is not associated with facebook.'))}
        response = json.dumps(res)
        return HttpResponse(response)
    async_check_like_yasound_on_facebook.apply_async(args=[request.user.id], countdown=60*3)
    res = {'success': True, 'message': unicode(_('Thank you, your gift will be available soon.'))}
    response = json.dumps(res)
    return HttpResponse(response)

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

