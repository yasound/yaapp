from celery.task import task
from models import UserProfile

import logging
logger = logging.getLogger("yaapp.account")

@task
def scan_friends_task():
    logger.debug('scan_friends_task')
    for profile in UserProfile.objects.all():
        profile.scan_friends()
        
@task
def check_live_status_task():
    for profile in UserProfile.objects.all():
        profile.check_live_status()