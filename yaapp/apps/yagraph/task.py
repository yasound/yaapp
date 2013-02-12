"""
Asynchronous tasks for managing Facebook Graph API actions.
"""

from account.models import UserProfile
from celery.task import task
from django.conf import settings
from django.core.urlresolvers import reverse
from facepy import GraphAPI
from yacore.http import absolute_url
import requests
import logging
logger = logging.getLogger("yaapp.yagraph")


def _facebook_token(user_id):
    try:
        user_profile = UserProfile.objects.get(user__id=user_id)
    except:
        logger.debug('cannot find profile for user %s' % (user_id))
        return None

    if not user_profile.facebook_enabled or len(user_profile.facebook_token) <= 0:
        logger.debug('user %d is not a facebook user or facebook token is not set' % (user_id))
        return None
    facebook_token = user_profile.facebook_token
    return facebook_token


@task(ignore_result=True)
def async_post_message(user_id, radio_uuid, message):
    logger.debug('async_post_message: user = %s, radio = %s, message = %s' % (user_id, radio_uuid, message))
    facebook_token = _facebook_token(user_id)
    if facebook_token is None:
        return

    radio_url = absolute_url(reverse('webapp_default_radio', args=[radio_uuid]))
    path = 'me/%s:post_message' % (settings.FACEBOOK_APP_NAMESPACE)

    graph = GraphAPI(facebook_token)
    try:
        res = graph.post(path=path, radio_station=radio_url)
        logger.debug(res)
    except GraphAPI.FacebookError, e:
        logger.error('async_post_message: %s' % e)
    except GraphAPI.HTTPError, e:
        logger.error('async_post_message: %s' % e)
    async_rescrape.apply_async(args=[radio_uuid], countdown=30)
    logger.debug('done')


@task(ignore_result=True)
def async_listen(user_id, radio_uuid, song_title, song_id):
    logger.debug('async_listen: user = %s, radio = %s, song = %s' % (user_id, radio_uuid, song_id))
    facebook_token = _facebook_token(user_id)
    if facebook_token is None:
        logger.debug('no facebook token, exiting')
        return

    radio_url = absolute_url(reverse('webapp_default_radio', args=[radio_uuid]))
    song_url = absolute_url(reverse('webapp_default_radio_song', args=[radio_uuid, song_id]))

    path = 'me/%s:play' % (settings.FACEBOOK_APP_NAMESPACE)

    logger.debug('calling graph api')
    graph = GraphAPI(facebook_token)
    try:
        res = graph.post(path=path, radio_station=radio_url, song=song_url)
        logger.debug(res)
    except GraphAPI.FacebookError, e:
        logger.error('async_listen: %s' % e)
    except GraphAPI.HTTPError, e:
        logger.error('async_listen: %s' % e)
    async_rescrape.apply_async(args=[radio_uuid, song_id], countdown=30)
    logger.debug('done')


@task(ignore_result=True)
def async_like_song(user_id, radio_uuid, song_title, song_id):
    logger.debug('async_like_song: user = %s, radio = %s, song = %s' % (user_id, radio_uuid, song_id))
    facebook_token = _facebook_token(user_id)
    if facebook_token is None:
        logger.debug('no facebook token for user %s' % (user_id))
        return

    song_url = absolute_url(reverse('webapp_default_radio_song', args=[radio_uuid, song_id]))
    path = 'me/og.likes'

    graph = GraphAPI(facebook_token)
    try:
        res = graph.post(path=path, object=song_url)
        logger.debug(res)
    except GraphAPI.FacebookError, e:
        logger.error('async_like_song: %s' % e)
    except GraphAPI.HTTPError, e:
        logger.error('async_like_song: %s' % e)
    async_rescrape.apply_async(args=[radio_uuid, song_id], countdown=30)


@task(ignore_result=True)
def async_animator_activity(user_id, radio_uuid):
    logger.debug('async_animator_activity: user = %s, radio = %s' % (user_id, radio_uuid))
    facebook_token = _facebook_token(user_id)
    if facebook_token is None:
        return

    radio_url = absolute_url(reverse('webapp_default_radio', args=[radio_uuid]))
    path = 'me/%s:update_programming' % (settings.FACEBOOK_APP_NAMESPACE)

    graph = GraphAPI(facebook_token)
    try:
        res = graph.post(path=path, radio_station=radio_url)
        logger.debug(res)
    except GraphAPI.FacebookError, e:
        logger.error('async_animator_activity: %s' % e)
    except GraphAPI.HTTPError, e:
        logger.error('async_animator_activity: %s' % e)
    async_rescrape.apply_async(args=[radio_uuid], countdown=30)


@task(rate_limit='50/s', ignore_result=True)
def async_rescrape(radio_uuid, song_id=None):
    """
    rescrape a facebook graph object to force a refresh.
    """

    if song_id is not None:
        url = absolute_url(reverse('webapp_default_radio_song', args=[radio_uuid, song_id]))
    else:
        url = absolute_url(reverse('webapp_default_radio', args=[radio_uuid]))

    params = {
        'id': url,
        'scrape': True
    }
    logger.debug('async_rescrape: params=%s' % (params))
    try:
        requests.post('https://graph.facebook.com', params=params)
    except Exception, e:
        logger.error('async_rescrape: %s' % e)
