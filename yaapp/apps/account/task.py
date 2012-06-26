from celery.task import task
from models import UserProfile
from django.core.cache import cache

import logging
logger = logging.getLogger("yaapp.account")

@task
def scan_friends_task():
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
    userprofile.set_position(coords[0], coords[1])