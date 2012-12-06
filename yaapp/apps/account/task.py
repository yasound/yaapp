from celery.task import task
from django.conf import settings
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from yacore.http import absolute_url
import logging
import tweepy
from django.utils import translation

logger = logging.getLogger("yaapp.account")


@task(ignore_result=True)
def scan_friends_task():
    from models import UserProfile

    logger.debug('scan_friends_task')
    total_friend_count = 0
    total_yasound_friend_count = 0
    for profile in UserProfile.objects.all():
        friend_count, yasound_friend_count = profile.scan_friends()
        total_friend_count += friend_count
        total_yasound_friend_count += yasound_friend_count

    cache.set('total_friend_count', total_friend_count)
    cache.set('total_yasound_friend_count', total_yasound_friend_count)


@task(ignore_result=True)
def check_live_status_task():
    from models import UserProfile

    for profile in UserProfile.objects.all():
        profile.check_live_status()


@task(ignore_result=True)
def async_check_geo_localization(userprofile, ip):
    logger.info('async_check_geo_localization')
    if userprofile.latitude is not None and userprofile.longitude is not None:
        return
    logger.info('async_check_geo_localization: need to use geoip to get latitude/longitude')
    from yacore.geoip import ip_coords
    coords = ip_coords(ip)
    if coords is None:
        return
    userprofile.set_position(coords[0], coords[1])


def _twitter_api(user_id):
    from models import UserProfile

    try:
        user_profile = UserProfile.objects.get(user__id=user_id)
    except:
        logger.debug('cannot find profile for user %s' % (user_id))
        return None

    if not user_profile.twitter_enabled:
        logger.debug('the user account %s is not twitter enabled' % (user_id))
        return None

    token = user_profile.twitter_token
    token_secret = user_profile.twitter_token_secret

    if token is None or token_secret is None:
        logger.debug('the user account %s is missing tokens' % (user_id))
        return None

    auth = tweepy.OAuthHandler(settings.YASOUND_TWITTER_APP_CONSUMER_KEY, settings.YASOUND_TWITTER_APP_CONSUMER_SECRET)
    auth.set_access_token(token, token_secret)
    api = tweepy.API(auth)
    res = api.verify_credentials()
    if res:
        return api
    else:
        logger.debug('wrong twitter credentials for user account %s' % (user_id))
        return None


def _set_language(user_id):
    from models import UserProfile
    user_profile = UserProfile.objects.get(user__id=user_id)
    language = user_profile.language
    translation.activate(language)


@task(ignore_result=True)
def async_tw_post_message(user_id, radio_uuid, message):
    logger.debug('async_tw_post_message: user = %s, radio = %s, message = %s' % (user_id, radio_uuid, message))
    api = _twitter_api(user_id)
    if api is None:
        logger.debug('no twitter api access for user %d' % (user_id))
        return

    _set_language(user_id)

    radio_url = absolute_url(reverse('webapp_default_radio', args=[radio_uuid]))
    tweet = _('I posted a message on %(url)s #yasound') % {'url': radio_url}
    try:
        api.update_status(status=tweet)
    except tweepy.error.TweepError, e:
        logger.error('async_tw_post_message: %s' % e)

    logger.debug('done')


@task(ignore_result=True)
def async_tw_listen(user_id, radio_uuid, song_title, artist):
    logger.debug('async_tw_listen: user = %s, radio = %s, song = %s' % (user_id, radio_uuid, song_title))
    api = _twitter_api(user_id)
    if api is None:
        logger.debug('no twitter api access for user %d' % (user_id))
        return

    _set_language(user_id)

    radio_url = absolute_url(reverse('webapp_default_radio', args=[radio_uuid]))
    tweet = _('I am listening to %(song)s by %(artist)s on %(url)s #yasound') % {'song': song_title[:7], 'artist': artist[:7], 'url': radio_url}
    try:
        api.update_status(status=tweet)
    except tweepy.error.TweepError, e:
        logger.error('async_tw_listen: %s' % e)

    logger.debug('done')


@task(ignore_result=True)
def async_tw_like_song(user_id, radio_uuid, song_title, artist):
    logger.debug('async_tw_like_song: user = %s, radio = %s, song = %s' % (user_id, radio_uuid, song_title))
    api = _twitter_api(user_id)
    if api is None:
        logger.debug('no twitter api access for user %d' % (user_id))
        return

    _set_language(user_id)

    radio_url = absolute_url(reverse('webapp_default_radio', args=[radio_uuid]))
    tweet = _('I like %(song)s by %(artist)s on %(url)s #yasound') % {'song': song_title[:7], 'artist': artist[:7], 'url': radio_url}
    try:
        api.update_status(status=tweet)
    except tweepy.error.TweepError, e:
        logger.error('async_tw_like_song: %s' % e)

    logger.debug('done')


@task(ignore_result=True)
def async_tw_animator_activity(user_id, radio_uuid):
    logger.debug('async_tw_animator_activity: user = %s, radio = %s' % (user_id, radio_uuid))
    api = _twitter_api(user_id)
    if api is None:
        logger.debug('no twitter api access for user %d' % (user_id))
        return

    _set_language(user_id)

    radio_url = absolute_url(reverse('webapp_default_radio', args=[radio_uuid]))
    tweet = _('I have updated my playist on %(url)s #yasound') % {'url': radio_url}
    try:
        api.update_status(status=tweet)
    except tweepy.error.TweepError, e:
        logger.error('async_tw_animator_activity: %s' % e)

    logger.debug('done')

