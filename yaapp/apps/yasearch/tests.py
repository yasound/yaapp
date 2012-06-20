from django.contrib.auth.models import User
from django.test import TestCase
from yabase import tests_utils as yabase_tests_utils
from yabase.models import Radio, SongInstance
from yasearch.models import MostPopularSongsManager

class TestMostPopularSong(TestCase):
    def setUp(self):
        manager = MostPopularSongsManager()
        manager.drop()
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
        
        
        