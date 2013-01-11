from django.conf import settings
import time
import datetime
from pymongo import DESCENDING
from yabase import signals as yabase_signals
from task import async_add_listen_activity, async_add_animator_activity
from dateutil.relativedelta import *
from django.core.cache import cache
from bson.objectid import ObjectId

import logging
logger = logging.getLogger("yaapp.yaactivity")

LOCK_EXPIRE = 60 * 1  # Lock expires in 1 minute(s)


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
            self.collection.remove(ObjectId(doc.get('_id')), safe=True)

    def add_friend_activity(self, user, friend, activity, **kwargs):
        now = datetime.datetime.now()
        if activity == FriendActivityManager.ACTIVITY_LISTEN:
            doc = {
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


class RadioActivityManager():
    WAIT_FOR_LOCK = 10  # wait 10 seconds

    ACTIVITY_UPDATE_PROGRAMMING = 'programming'
    MAX_ACTIVITY_PER_USER = 100

    def __init__(self):
        self.db = settings.MONGO_DB
        self.collection = self.db.activity.radio
        self.collection.ensure_index('user.username')
        self.collection.ensure_index('radio.uuid')
        self.collection.ensure_index('activity')
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
        res = self.collection.find({'user.username': user.username}, safe=True).sort([('updated', DESCENDING)]).skip(RadioActivityManager.MAX_ACTIVITY_PER_USER)
        for doc in res:
            self.collection.remove(ObjectId(doc.get('_id')), safe=True)

    def add_radio_activity(self, user, radio, activity, **kwargs):
        lock_id = "radio-activity-%s" % (radio.uuid)
        acquire_lock = lambda: cache.add(lock_id, "true", LOCK_EXPIRE)
        release_lock = lambda: cache.delete(lock_id)

        retry = 0
        max_retry = 3
        while not acquire_lock():
            time.sleep(RadioActivityManager.WAIT_FOR_LOCK)
            retry += 1
            if retry > max_retry:
                return

        now = datetime.datetime.now()
        if activity == RadioActivityManager.ACTIVITY_UPDATE_PROGRAMMING:
            last_hour = now - relativedelta(hour=1)
            filter = {
                'user.username': user.username,
                'radio.uuid': radio.uuid,
                'created': {
                    '$gte': last_hour
                }
            }
            doc = self.collection.find_one(filter)
            if doc is None:
                doc = {
                    'user': self._user_doc(user),
                    'radio': self._radio_doc(radio),
                    'activity': activity,
                    'created': now,
                }
                self.collection.insert(doc, safe=True)
            self.remove_obsolete_data_for_user(user)
        release_lock()

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


def new_animator_activity_handler(sender, user, radio, atype, details=None, **kwargs):
    if radio is not None:
        async_add_animator_activity.delay(radio.id, atype, details=details)


def install_handlers():
    yabase_signals.user_started_listening.connect(user_started_listening_handler)
    yabase_signals.new_animator_activity.connect(new_animator_activity_handler)

install_handlers()
