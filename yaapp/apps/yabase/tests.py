from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from models import NextSong, SongInstance, RADIO_NEXT_SONGS_COUNT, Radio, \
    RadioUser
from tests_utils import generate_playlist
from yabase.models import FeaturedContent
from yaref.models import YasoundAlbum, YasoundSong, YasoundArtist
import settings as yabase_settings

class TestDatabase(TestCase):
    multi_db = True
    fixtures = ['yasound_local.yaml',]
    def setUp(self):
        user = User(email="test@yasound.com", username="test", is_superuser=False, is_staff=False)
        user.set_password('test')
        user.save()
        self.client.login(username="test", password="test")
        self.user = user        
    
    def testFixtures(self):
        song = YasoundSong.objects.get(id=1)
        self.assertEqual(song.id, 1)

class TestModels(TestCase):
    def setUp(self):
        user = User(email="test@yasound.com", username="test", is_superuser=False, is_staff=False)
        user.set_password('test')
        user.save()
        self.client.login(username="test", password="test")
        self.user = user        
    
        # build some data
        radio = Radio(creator=user, name='radio1')
        radio.save()
        self.radio = radio
        
    def testRadioUser(self):
        connected = RadioUser.objects.get_connected()
        self.assertEquals(len(connected), 0)
        
        ru = RadioUser(radio=self.radio, user=self.user)
        ru.save()
        
        # test default fields
        self.assertEquals(ru.mood, yabase_settings.MOOD_NEUTRAL)
        
        # test favorite
        favorites = RadioUser.objects.get_favorite()
        self.assertEquals(len(favorites), 0)
        
        ru.favorite = True
        ru.save()

        favorites = RadioUser.objects.get_favorite()
        self.assertEquals(len(favorites), 1)
        
        # test likers
        likers = RadioUser.objects.get_likers()
        self.assertEquals(len(likers), 0)
        
        ru.mood = yabase_settings.MOOD_LIKE
        ru.save()

        likers = RadioUser.objects.get_likers()
        self.assertEquals(len(likers), 1)

        # test dislikers
        dislikers = RadioUser.objects.get_dislikers()
        self.assertEquals(len(dislikers), 0)
        
        ru.mood = yabase_settings.MOOD_DISLIKE
        ru.save()

        dislikers = RadioUser.objects.get_dislikers()
        self.assertEquals(len(dislikers), 1)

        # misc fields
        self.assertEquals(dislikers[0].radio, self.radio)
        self.assertEquals(dislikers[0].user, self.user)
   
class TestNextSong(TestCase):
    multi_db = True
    fixtures = ['yasound_local.yaml',]
    def setUp(self):
        user = User(email="test@yasound.com", username="test", is_superuser=False, is_staff=False)
        user.set_password('test')
        user.save()
        self.client.login(username="test", password="test")
        self.user = user        
    
        # build some data
        radio = Radio(creator=user, name='radio1', uuid='radio1')
        radio.save()
        self.radio = radio
        
    def test_view_empty_radio(self):
        res = self.client.get(reverse('yabase.views.get_next_song', args=['radio1']))
        self.assertEqual(res.status_code, 404)

    def test_view_not_empty_radio(self):
        playlist = generate_playlist(song_count=5)
        self.radio.playlists.add(playlist)

        ns = NextSong(song=SongInstance.objects.get(id=1), radio=self.radio, order=1)
        ns.save()
        self.assertEqual(self.radio.next_songs.count(), 1)

        res = self.client.get(reverse('yabase.views.get_next_song', args=['radio1']))
        self.assertEqual(res.status_code, 200)

        res = self.client.get(reverse('yabase.views.get_next_song', args=['radio1']))
        self.assertEqual(res.status_code, 200)
        
    def test_find_new_song(self):
        playlist = generate_playlist(song_count=5)
        self.radio.playlists.add(playlist)
        song = self.radio.find_new_song()
        self.assertIn(song.id, range(0, 6))
        
    def test_empty_next_songs_queue(self):
        playlist = generate_playlist(song_count=5)
        self.radio.playlists.add(playlist)

        ns = NextSong(song=SongInstance.objects.get(id=1), radio=self.radio, order=1)
        ns.save()
        self.assertEqual(self.radio.next_songs.count(), 1)
        self.radio.empty_next_songs_queue()
        self.assertEqual(self.radio.next_songs.count(), 0)
        
class TestFuzzy(TestCase):
    multi_db = True
    fixtures = ['yasound_local.yaml',]
    def setUp(self):
        user = User(email="test@yasound.com", username="test", is_superuser=False, is_staff=False)
        user.set_password('test')
        user.save()
        self.client.login(username="test", password="test")
        self.user = user        
    
        # build some data
        
        radio = Radio(creator=user, name='radio1', uuid='radio1')
        radio.save()
        self.radio = radio
        
    def test_search(self):
        song = u'party'
        artist = u'The English Beat'
        album = u'Special'
        best_song = YasoundSong.objects.find_fuzzy(song, album, artist, limit=1)
        
    def test_search2(self):
        song = u'live village'
        artist = u'chris'
        album = u''
        best_song = YasoundSong.objects.find_fuzzy(song, album, artist, limit=1)
        
class TestFeaturedModels(TestCase):
    multi_db = True
    fixtures = ['yasound_local.yaml',]
    def setUp(self):
        user = User(email="test@yasound.com", username="test", is_superuser=False, is_staff=False)
        user.set_password('test')
        user.save()
        self.client.login(username="test", password="test")
        self.user = user        
    
        # build some data
        radio = Radio(creator=user, name='radio1', uuid='radio1')
        radio.save()
        self.radio = radio
    
    def testActivate(self):
        featured_content1 = FeaturedContent(name='featured_1') 
        featured_content1.save()
        
        self.assertEquals(featured_content1.activated, False)
        
        featured_content1.activated = True
        featured_content1.save()
        self.assertEquals(featured_content1.activated, True)
        
        featured_content2 = FeaturedContent(name='featured_2') 
        featured_content2.save()
        featured_content1 = FeaturedContent.objects.get(id=featured_content1.id)
        featured_content2 = FeaturedContent.objects.get(id=featured_content2.id)
        self.assertEquals(featured_content1.activated, True)
        self.assertEquals(featured_content2.activated, False)

        featured_content2.activated = True
        featured_content2.save()
        featured_content1 = FeaturedContent.objects.get(id=featured_content1.id)
        featured_content2 = FeaturedContent.objects.get(id=featured_content2.id)
        self.assertEquals(featured_content1.activated, False)
        self.assertEquals(featured_content2.activated, True)
        featured_content1.activated = True
        featured_content1.save()
        featured_content1 = FeaturedContent.objects.get(id=featured_content1.id)
        featured_content2 = FeaturedContent.objects.get(id=featured_content2.id)
        self.assertEquals(featured_content1.activated, True)
        self.assertEquals(featured_content2.activated, False)
        
           
