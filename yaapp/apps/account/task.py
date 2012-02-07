from celery.task import task
from models import UserProfile

@task
def scan_friends_task():
    print 'scan_friends_task'
    for profile in UserProfile.objects.all():
        profile.scan_friends()