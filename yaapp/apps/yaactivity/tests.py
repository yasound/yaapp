from django.test import TestCase
from models import FriendActivityManager
from django.contrib.auth.models import User
from task import async_add_listen_activity
from yabase.models import Radio


class TestWallManager(TestCase):
    def setUp(self):
        m = FriendActivityManager()
        m.collection.drop()

    def test_add_event(self):
        m = FriendActivityManager()

        user = User.objects.create(email="test@yasound.com", username="test", is_superuser=False, is_staff=False)
        friend = User.objects.create(email="friend@yasound.com", username="friend", is_superuser=False, is_staff=False)
        radio = Radio.objects.create(creator=user)

        activities = m.activities_for_user(user=user)
        self.assertEquals(activities.count(), 0)

        m.add_friend_activity(user=user, friend=friend, activity=FriendActivityManager.ACTIVITY_LISTEN, radio=radio)

        activities = m.activities_for_user(user=user)
        self.assertEquals(activities.count(), 1)


    def test_task_add_event(self):
        m = FriendActivityManager()

        user = User.objects.create(email="test@yasound.com", username="test", is_superuser=False, is_staff=False)
        friend = User.objects.create(email="friend@yasound.com", username="friend", is_superuser=False, is_staff=False)
        user.get_profile().friends.add(friend)
        radio = Radio.objects.create(creator=user)

        async_add_listen_activity(user.id, radio.id)

        activities = m.activities_for_user(user=user)
        self.assertEquals(activities.count(), 0)

        activities = m.activities_for_user(user=friend)
        self.assertEquals(activities.count(), 1)
