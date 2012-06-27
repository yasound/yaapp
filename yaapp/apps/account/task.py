from celery.task import task
from django.conf import settings
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.urlresolvers import reverse
from yacore.http import absolute_url
import logging
import tweepy

logger = logging.getLogger("yaapp.account")

@task
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
        
@task
def check_live_status_task():
    from models import UserProfile
    
    for profile in UserProfile.objects.all():
        profile.check_live_status()
        
@task 
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

    user = User.objects.get(id=user_id)
    if not user.is_superuser:
        return None
    
    try:
        user_profile = UserProfile.objects.get(user__id=user_id)
    except:
        logger.debug('cannot find profile for user %s' % (user_id))
        return None
    
    if user_profile.twitter_enabled:
        return None
    
    token = user_profile.twitter_token
    token_secret = user_profile.twitter_token_secret
    
    if token is None or token_secret is None:
        return None
    
    auth = tweepy.OAuthHandler(settings.YASOUND_TWITTER_APP_CONSUMER_KEY, settings.YASOUND_TWITTER_APP_CONSUMER_SECRET)
    auth.set_access_token(token, token_secret)
    api = tweepy.API(auth)
    res = api.verify_credentials()
    if res:
        return api
    else:
        return None
    
@task(ignore_result=True)
def async_tw_post_message(user_id, radio_uuid, message):
    logger.debug('async_tw_post_message: user = %s, radio = %s, message = %s' % (user_id, radio_uuid, message))
    api = _twitter_api(user_id)
    if api is None:
        return
    
    radio_url = absolute_url(reverse('webapp_radio', args=[radio_uuid])) 
    logger.debug('done')
    
@task(ignore_result=True)
def async_tw_listen(user_id, radio_uuid, song_title, song_id):
    logger.debug('async_tw_listen: user = %s, radio = %s, song = %s' % (user_id, radio_uuid, song_title))
    api = _twitter_api(user_id)
    if api is None:
        return
    
    radio_url = absolute_url(reverse('webapp_radio', args=[radio_uuid])) 
    logger.debug('done')

@task(ignore_result=True)
def async_tw_like_song(user_id, radio_uuid, song_title, song_id):
    logger.debug('async_tw_like_song: user = %s, radio = %s, song = %s' % (user_id, radio_uuid, song_title))
    api = _twitter_api(user_id)
    if api is None:
        return

    radio_url = absolute_url(reverse('webapp_radio', args=[radio_uuid])) 
    song_url = absolute_url(reverse('yabase.views.web_song', args=[radio_uuid, song_id]))
    logger.debug('done')
        
@task(ignore_result=True)
def async_tw_animator_activity(user_id, radio_uuid):
    logger.debug('async_tw_animator_activity: user = %s, radio = %s' % (user_id, radio_uuid))
    api = _twitter_api(user_id)
    if api is None:
        return

    radio_url = absolute_url(reverse('webapp_radio', args=[radio_uuid])) 

    logger.debug('done')


@task(ignore_result=True)
def async_update_position_coords(userprofile):
    userprofile.update_position_coords()

