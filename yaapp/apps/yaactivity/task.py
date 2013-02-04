from celery.task import task
import logging
from django.contrib.auth.models import User
from yabase.models import Radio, RadioUser

logger = logging.getLogger("yaapp.yaactivity")


@task(ignore_result=True)
def async_add_listen_activity(user_id, radio_id):
    user = User.objects.get(id=user_id)
    profile = user.get_profile()
    radio = Radio.objects.get(id=radio_id)

    from models import FriendActivityManager
    m = FriendActivityManager()
    friends = profile.friends.all()
    for friend in friends:
        m.add_friend_activity(user=friend, friend=user, activity=FriendActivityManager.ACTIVITY_LISTEN, radio=radio)


@task(ignore_result=True)
def async_add_animator_activity(radio_id, atype, details):
    try:
        radio = Radio.objects.get(id=radio_id)
    except Radio.DoesNotExist:
        return

    from models import RadioActivityManager
    m = RadioActivityManager()

    rus = RadioUser.objects.select_related('user').filter(radio=radio, favorite=True)
    for ruser in rus:
        m.add_radio_activity(user=ruser.user, radio=radio, activity=RadioActivityManager.ACTIVITY_UPDATE_PROGRAMMING)
