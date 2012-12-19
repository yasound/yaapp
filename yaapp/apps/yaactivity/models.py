from django.conf import settings
import datetime
from pymongo import DESCENDING
from yabase import signals as yabase_signals
from task import async_add_listen_activity
import logging
logger = logging.getLogger("yaapp.yaactivity")


class FriendActivityManager():
    ACTIVITY_LISTEN = 'listen'
    MAX_ACTIVITY_PER_USER = 100

    def __init__(self):
        self.db = settings.MONGO_DB
        self.collection = self.db.activity.friend
        self.collection.ensure_index('user.username')
        self.collection.ensure_index('friend.username')
        self.collection.ensure_index('created')

    def _user_doc(self, user):
        return {
            'name': unicode(user.get_profile()),
            'username': user.username,
        }

    def _radio_doc(self, radio):
        return {
            'uuid': radio.uuid,
            'name': radio.name,
        }

    def remove_obsolete_data_for_user(self, user):
        res = self.collection.find({'user.username': user.username}, safe=True).sort([('updated', DESCENDING)]).skip(FriendActivityManager.MAX_ACTIVITY_PER_USER)
        for doc in res:
            doc.remove(safe=True)

    def add_friend_activity(self, user, friend, activity, **kwargs):
        now = datetime.datetime.now()
        if activity == FriendActivityManager.ACTIVITY_LISTEN:
            doc = {
                'friend': friend.username,
                'user': self._user_doc(user),
                'friend': self._user_doc(friend),
                'radio': self._radio_doc(kwargs.get('radio')),
                'activity': activity,
                'created': now
            }

            self.collection.insert(doc, safe=True)
            self.remove_obsolete_data_for_user(user)

    def activities_for_user(self, user, activity=None, limit=10, skip=0):
        filter = {
            'user.username': user.username
        }
        if activity is not None:
            filter['activity'] = activity
        return self.collection.find(filter).sort([('updated', DESCENDING)]).skip(skip).limit(limit)


def user_started_listening_handler(sender, radio, user, **kwargs):
    if not user.is_anonymous():
        async_add_listen_activity.delay(user.id, radio.id)


def install_handlers():
    yabase_signals.user_started_listening.connect(user_started_listening_handler)
install_handlers()
