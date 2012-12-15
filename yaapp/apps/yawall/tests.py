from django.test import TestCase
from models import WallManager
from django.contrib.auth.models import User
from yabase.models import Radio


class TestWallManager(TestCase):
    def setUp(self):
        w = WallManager()
        w.collection.drop()

    def test_add_event(self):
        w = WallManager()

        user = User.objects.create(email="test@yasound.com", username="test", is_superuser=False, is_staff=False)
        radio = Radio.objects.create(creator=user)

        w.add_event(event_type=WallManager.EVENT_MESSAGE, radio=radio, user=user, message='hello, world')

        events = w.events_for_radio(radio.uuid)
        self.assertEquals(events.count(), 1)