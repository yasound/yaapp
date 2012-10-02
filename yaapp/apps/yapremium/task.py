from django.contrib.auth.models import User
from celery.task import task
from datetime import *
from account.models import UserProfile, InvitationsManager
import settings as yapremium_settings


@task
def check_expiration_date():
    from models import UserService
    today = date.today()
    uss = UserService.objects.filter(expiration_date__lt=today, active=True)
    for us in uss:
        us.active = False
        us.save()


@task
def async_win_gift(user_id, action):
    from models import Gift, Achievement
    user = User.objects.get(id=user_id)
    gifts = Gift.objects.filter(action=action, enabled=True)

    for gift in gifts:
        if gift.available(user):
            # yipee ! gift is won
            Achievement.objects.create_from_gift(user=user, gift=gift)


@task
def async_check_for_invitation(type, uid):
    ia = InvitationsManager()
    users = ia.find_invitation_providers(type, uid)
    for user in users:
        user_id = user.get('db_id')
        async_win_gift.delay(user_id, yapremium_settings.ACTION_INVITE_FRIEND)
