from celery.task import task
import logging
from django.contrib.auth.models import User
from yabase.models import Radio

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
