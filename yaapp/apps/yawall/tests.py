from django.test import TestCase
from models import WallManager
from django.contrib.auth.models import User
from yabase.models import Radio, SongInstance, WallEvent
from yabase import settings as yabase_settings
from yasearch.indexer import erase_index, add_song
from django.core.urlresolvers import reverse
from mock import Mock, patch
from yabase.tests_utils import generate_playlist

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


class TestCreate(TestCase):
    def setUp(self):
        w = WallManager()
        w.collection.drop()

        erase_index()
        user = User(email="test@yasound.com", username="test", is_superuser=True, is_staff=True)
        user.set_password('test')
        user.save()
        Radio.objects.create(creator=user)
        self.client.login(username="test", password="test")
        self.user = user
        self.username = self.user.username

        radio = Radio.objects.radio_for_user(self.user)
        playlist = generate_playlist(song_count=100)
        playlist.radio = radio
        playlist.save()

        self.radio = radio
        self.radio.current_song = SongInstance.objects.filter(playlist=playlist).order_by('?')[0]
        self.radio.save()

    def test_like_song(self):
        w = WallManager()
        redis = Mock(name='redis')
        redis.publish = Mock()
        with patch('yabase.push.Redis') as mock_redis:
            mock_redis.return_value = redis
            song = SongInstance.objects.get(id=1)

            self.client.post(reverse('yabase.views.like_song', args=[song.id]))
            self.assertEquals(WallEvent.objects.filter(type=yabase_settings.EVENT_LIKE).count(), 1)

            events = w.events_for_radio(song.playlist.radio.uuid)
            self.assertEquals(events.count(), 1)

    def test_post_message(self):
        w = WallManager()
        redis = Mock(name='redis')
        redis.publish = Mock()
        with patch('yabase.push.Redis') as mock_redis:
            mock_redis.return_value = redis

            # post message
            res = self.client.post(reverse('yabase.views.post_message', args=[self.radio.uuid]), {'message': 'hello, world'})
            self.assertEquals(res.status_code, 200)
            self.assertEquals(WallEvent.objects.filter(type=yabase_settings.EVENT_MESSAGE).count(), 1)
            self.assertEquals(WallEvent.objects.filter(type=yabase_settings.EVENT_SONG).count(), 1)

            events = w.events_for_radio(self.radio.uuid)
            self.assertEquals(events.count(), 1)

            # delete posted message
            message = WallEvent.objects.filter(type=yabase_settings.EVENT_MESSAGE)[0]

            res = self.client.delete(reverse('yabase.views.delete_message', args=[message.id]))
            self.assertEquals(res.status_code, 200)
            self.assertEquals(WallEvent.objects.filter(type=yabase_settings.EVENT_MESSAGE).count(), 0)
            self.assertEquals(WallEvent.objects.filter(type=yabase_settings.EVENT_SONG).count(), 1)

            events = w.events_for_radio(self.radio.uuid)
            self.assertEquals(events.count(), 0)

            # post to another radio
            other_radio = Radio.objects.create(name='other')
            res = self.client.post(reverse('yabase.views.post_message', args=[other_radio.uuid]), {'message': 'hello, world'})
            self.assertEquals(res.status_code, 200)
            self.assertEquals(WallEvent.objects.filter(type=yabase_settings.EVENT_MESSAGE).count(), 1)
            self.assertEquals(WallEvent.objects.filter(type=yabase_settings.EVENT_SONG).count(), 1)

            events = w.events_for_radio(other_radio.uuid)
            self.assertEquals(events.count(), 1)

            # delete posted message : impossible because user is not the owner of radio
            message = WallEvent.objects.filter(type=yabase_settings.EVENT_MESSAGE, radio=other_radio)[0]

            res = self.client.delete(reverse('yabase.views.delete_message', args=[message.id]))
            self.assertEquals(res.status_code, 401)

            events = w.events_for_radio(other_radio.uuid)
            self.assertEquals(events.count(), 1)
