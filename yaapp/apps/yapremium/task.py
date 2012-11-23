from django.contrib.auth.models import User
from celery.task import task
from datetime import *
from account.models import UserProfile, InvitationsManager
import settings as yapremium_settings
from django.conf import settings
import logging
import tweepy
from facepy import GraphAPI
logger = logging.getLogger("yaapp.yapremium")


@task
def check_expiration_date():
    from models import UserService
    today = date.today()
    uss = UserService.objects.filter(expiration_date__lt=today, active=True)
    for us in uss:
        us.active = False
        us.save()


@task
def async_win_gift(user_id, action, dont_give_anything=False):
    logger.debug('checking gift/action for user %s, action=%s' % (user_id, action))
    from models import Gift, Achievement
    user = User.objects.get(id=user_id)
    gifts = Gift.objects.filter(action=action, enabled=True)

    for gift in gifts:
        if gift.available(user):
            # yipee ! gift is won
            Achievement.objects.create_from_gift(user=user, gift=gift, dont_give_anything=dont_give_anything)


@task
def async_check_for_invitation(type, uid):
    ia = InvitationsManager()
    logger.info('checking for invitation for type = %s, uid = %s' % (type, uid))
    users = ia.find_invitation_providers(type, uid)
    for user in users:
        user_id = user.get('db_id')
        logger.info('and the winner is %s' % (user_id))
        async_win_gift.delay(user_id, yapremium_settings.ACTION_INVITE_FRIENDS)


@task
def async_check_follow_yasound_on_twitter(user_id, yasound_twitter_account):
    profile = UserProfile.objects.get(user__id=user_id)
    if not profile.twitter_enabled:
        return

    auth = tweepy.OAuthHandler(settings.YASOUND_TWITTER_APP_CONSUMER_KEY, settings.YASOUND_TWITTER_APP_CONSUMER_SECRET)
    auth.set_access_token(profile.twitter_token, profile.twitter_token_secret)
    api = tweepy.API(auth)
    friends = api.lookup_users(screen_names=[yasound_twitter_account])
    if len(friends) > 0:
        yasound = friends[0]
        if yasound.following:
            async_win_gift(user_id, yapremium_settings.ACTION_FOLLOW_YASOUND_TWITTER)


@task
def async_check_like_yasound_on_facebook(user_id):
    profile = UserProfile.objects.get(user__id=user_id)
    if not profile.facebook_enabled:
        return

    facebook_token = profile.facebook_token
    if facebook_token is None:
        return

    path = 'me/likes/%s' % (settings.FACEBOOK_PAGE_ID)
    graph = GraphAPI(facebook_token)
    try:
        res = graph.get(path=path)
        logger.debug(res)
        if len(res.get('data', [])) != 0:
            async_win_gift(user_id, yapremium_settings.ACTION_LIKE_YASOUND_FACEBOOK)
    except GraphAPI.FacebookError as e:
        logger.info(e)
    logger.debug('done')
