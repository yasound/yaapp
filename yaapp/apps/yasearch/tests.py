from django.contrib.auth.models import User
from django.test import TestCase
from yabase import tests_utils as yabase_tests_utils
from yabase.models import Radio, SongInstance
from models import MostPopularSongsManager, RadiosManager
from yaref import test_utils as yaref_test_utils
from yaref.models import YasoundSong
from yabase import signals as yabase_signals

class TestMostPopularSong(TestCase):
    def setUp(self):
        manager = MostPopularSongsManager()
        manager.drop()
        YasoundSong.objects.all().delete()
        user = User(email="test@yasound.com", username="test", is_superuser=False, is_staff=False)
        user.set_password('test')
        user.save()
        self.client.login(username="test", password="test")
        self.user = user

    def test_add_song(self):
        radio = Radio.objects.radio_for_user(self.user)
        playlist = yabase_tests_utils.generate_playlist()
        playlist.radio = radio
        playlist.save()

        manager = MostPopularSongsManager()
        self.assertEquals(manager.all().count(), 5)

        song_instance = SongInstance.objects.all()[6]
        other_song_instance = SongInstance.objects.create(metadata=song_instance.metadata, playlist=playlist)

        self.assertEquals(manager.all().count(), 5)

        docs = manager.all()
        self.assertEquals(docs[0].get('songinstance__count'), 2)
        self.assertEquals(docs[1].get('songinstance__count'), 1)

        song_instance = SongInstance.objects.all()[7]
        for _i in range(0, 10):
            SongInstance.objects.create(metadata=song_instance.metadata, playlist=playlist)
        docs = manager.all()
        self.assertEquals(docs[0].get('songinstance__count'), 11)
        self.assertEquals(manager.all().count(), 5)

        manager.populate()
        docs = manager.all()
        self.assertEquals(docs[0].get('songinstance__count'), 11)
        self.assertEquals(manager.all().count(), 5)

        song_instance.delete()
        docs = manager.all()
        self.assertEquals(docs[0].get('songinstance__count'), 10)

class TestRadio(TestCase):

    def setUp(self):
        manager = RadiosManager()
        manager.drop()
        YasoundSong.objects.all().delete()
        self.manager = manager
        user = User(email="test@yasound.com", username="test", is_superuser=False, is_staff=False)
        user.set_password('test')
        user.save()
        self.client.login(username="test", password="test")
        self.user = user

    def test_basic_search(self):
        res = self.manager.search('radio1')
        self.assertEquals(len(res), 0)

        radio = Radio.objects.create(name='radio1', ready=True, creator=self.user)
        playlist = yabase_tests_utils.generate_playlist()
        playlist.radio = radio
        playlist.save()
        res = self.manager.search('radio1')
        self.assertEquals(len(res), 1)

        yaref_test_utils.generate_yasound_song(name='song', artist='artist', album='album')
        radio.set_current_song(SongInstance.objects.get(id=1))

        res = self.manager.search('artist')
        self.assertEquals(len(res), 1)

    def test_basic_search_artist_with_space(self):
        res = self.manager.search('radio1')
        self.assertEquals(len(res), 0)

        radio = Radio.objects.create(name='radio1', ready=True, creator=self.user)
        playlist = yabase_tests_utils.generate_playlist()
        playlist.radio = radio
        playlist.save()
        res = self.manager.search('radio1')
        self.assertEquals(len(res), 1)

        yaref_test_utils.generate_yasound_song(name='song', artist='the cure', album='album')
        radio.set_current_song(SongInstance.objects.get(id=1))

        res = self.manager.search('the cure')
        self.assertEquals(len(res), 1)

    def test_search_artist_name(self):
        res = self.manager.search('radio1')
        self.assertEquals(len(res), 0)

        radio1 = Radio.objects.create(name='radio1', ready=True, creator=self.user)
        playlist = yabase_tests_utils.generate_playlist()
        playlist.radio = radio1
        playlist.save()

        yaref_test_utils.generate_yasound_song(name='song', artist='artist', album='album')
        radio1.set_current_song(SongInstance.objects.get(id=1))

        radio2 = Radio.objects.create(name='artist', ready=True, creator=self.user)
        playlist = yabase_tests_utils.generate_playlist()
        playlist.radio2 = radio2
        playlist.save()

        res = self.manager.search('artist')
        self.assertEquals(len(res), 2)

        self.assertEquals(res[0].id, radio1.id)

    def test_search_by_song(self):
        res = self.manager.search('radio1')
        self.assertEquals(len(res), 0)

        radio1 = Radio.objects.create(name='radio1', ready=True, creator=self.user)
        playlist = yabase_tests_utils.generate_playlist()
        playlist.radio = radio1
        playlist.save()

        yaref_test_utils.generate_yasound_song(name='song', artist='artist', album='album')
        radio1.set_current_song(SongInstance.objects.get(id=1))

        radio2 = Radio.objects.create(name='artist', ready=True, creator=self.user)
        playlist = yabase_tests_utils.generate_playlist()
        playlist.radio2 = radio2
        playlist.save()

        res = self.manager.search_by_current_song('artist')
        self.assertEquals(len(res), 1)

        self.assertEquals(res[0].id, radio1.id)

