from django.contrib.auth.models import User
from celery.task import task
from datetime import *


@task
def check_expiration_date():
    from models import UserService
    today = date.today()
    uss = UserService.objects.filter(expiration_date__lt=today, active=True)
    for us in uss:
        us.active = False
        us.save()


@task
def async_check_gift(user_id, action):
    from models import Gift, Achievement
    user = User.objects.get(id=user_id)
    gifts = Gift.objects.filter(action=action, enabled=True)

    for gift in gifts:
        if gift.available(user):
            Achievement.objects.create_from_gift(user=user, gift=gift)
