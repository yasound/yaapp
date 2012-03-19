from django.contrib.auth.models import User
from django.core.files import File
from django.core.urlresolvers import reverse
from django.db.models.aggregates import Count
from django.test import TestCase
from models import NextSong, SongInstance, RADIO_NEXT_SONGS_COUNT, Radio, \
    RadioUser
from task import process_playlists_exec
from tests_utils import generate_playlist
from yabase.import_utils import SongImporter, generate_default_filename
from yabase.models import FeaturedContent, Playlist, SongMetadata
from yaref import test_utils as yaref_test_utils
from yaref.models import YasoundAlbum, YasoundSong, YasoundArtist
from yasearch.indexer import erase_index, add_song
import import_utils
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
        
    def testUUID(self):
        self.assertTrue(self.radio.uuid is not None)
        
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
        
    def test_default_playlist(self):
        playlist, created = self.radio.get_or_create_default_playlist()
        
        self.assertTrue(created)
        self.assertTrue(playlist.enabled)
        self.assertEquals(playlist.name, u'default')
        
        default_playlist = self.radio.default_playlist
        self.assertEquals(default_playlist, playlist)
        
        other_playlist = Playlist(name='other_playlist', radio=self.radio, enabled=False)
        other_playlist.save()

        default_playlist = self.radio.default_playlist
        self.assertEquals(default_playlist, playlist)

        default_playlist.delete()
        playlist, created = self.radio.get_or_create_default_playlist()
        self.assertTrue(created)
        self.assertEquals(playlist.name, u'default')
        
    def test_migrate_playlist(self):
        playlist1 = generate_playlist(name='playlist1', song_count=30)
        playlist2 = generate_playlist(name='playlist2', song_count=30)
        playlist3 = generate_playlist(name='playlist3', song_count=30)
        
        playlist1.radio = self.radio
        playlist2.radio = self.radio
        playlist3.radio = self.radio
        
        playlist1.save()
        playlist2.save()
        playlist3.save()
        
        # dry effect, nothing is altered
        self.radio = Radio.objects.get(id=self.radio.id)
        self.assertEquals(self.radio.playlists.count(), 3)
        self.assertEquals(SongInstance.objects.all().count(), 30*3)
        Playlist.objects.migrate_songs_to_default(dry=True)
        
        playlist1 = Playlist.objects.get(name='playlist1')
        self.assertEquals(playlist1.song_count, 30)
        
        # no dry effect, a single playlist should be created
        Playlist.objects.migrate_songs_to_default(dry=False)
        self.radio = Radio.objects.get(id=self.radio.id)
        self.assertEquals(self.radio.playlists.count(), 1)
        self.assertEquals(SongInstance.objects.all().count(), 30*3)
        self.assertEquals(self.radio.default_playlist.song_count, 30*3)

        # same as previous, nothing has changed
        Playlist.objects.migrate_songs_to_default(dry=False)
        self.radio = Radio.objects.get(id=self.radio.id)
        self.assertEquals(self.radio.playlists.count(), 1)
        self.assertEquals(SongInstance.objects.all().count(), 30*3)
        self.assertEquals(self.radio.default_playlist.song_count, 30*3)
        
   
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
        
class TestImportPlaylist(TestCase):
    def setUp(self):
        user = User(email="test@yasound.com", username="test", is_superuser=False, is_staff=False)
        user.set_password('test')
        user.save()
        self.client.login(username="test", password="test")
        self.user = user     
        erase_index()   
    
    def test_import_empty(self):
        radio = Radio.objects.radio_for_user(self.user)
        process_playlists_exec(radio, content_compressed=None)

    def test_import_ok_with_nothing_found(self):
        radio = Radio.objects.radio_for_user(self.user)
        
        # 643 songs with some duplicates, 492 unique songs
        f = open('./apps/yabase/fixtures/playlist.data')
        content_compressed = f.read()
        f.close()

        self.assertEquals(SongInstance.objects.all().count(), 0)
        process_playlists_exec(radio, content_compressed=content_compressed)
        self.assertEquals(SongInstance.objects.all().count(), 492)
        self.assertEquals(SongMetadata.objects.filter(yasound_song_id__isnull=True).count(), 492)
        
    def test_import_ok_with_references(self):
        radio = Radio.objects.radio_for_user(self.user)
        f = open('./apps/yabase/fixtures/playlist.data')
        content_compressed = f.read()
        f.close()

        song = yaref_test_utils.generate_yasound_song('one of a kind', 'meds', 'placebo')
        add_song(song)
        self.assertEquals(SongInstance.objects.all().count(), 0)
        process_playlists_exec(radio, content_compressed=content_compressed)
        self.assertEquals(SongInstance.objects.all().count(), 492)
        self.assertEquals(SongMetadata.objects.filter(yasound_song_id__isnull=True).count(), 491)
     
        tests = SongMetadata.objects.annotate(num=Count('songinstance'))
        for test in tests:
            if test.num >= 3:
                print u'%d: %s: %d' % (test.id, test, test.num)
                sis = SongInstance.objects.filter(metadata=test)
                for si in sis:
                    print u'%d:%s:%d' % (si.id, si, si.order)
     
class TestImport(TestCase):
    def setUp(self):
        user = User(email="test@yasound.com", username="test", is_superuser=False, is_staff=False)
        user.set_password('test')
        user.save()
        self.client.login(username="test", password="test")
        self.user = user     
        erase_index()   
    
    def test_quality(self):
        metadata = {'bitrate': '10',
                    'lastfm_id': None,
                    'echonest_id': None,
        }
        importer = SongImporter()
        quality = importer._get_quality(metadata) 
        self.assertEquals(quality, 0)
        
        metadata = {'bitrate': '192',
                    'lastfm_id': None,
                    'echonest_id': None,
        }
        quality = importer._get_quality(metadata) 
        self.assertEquals(quality, 100)
        
        metadata = {'bitrate': '192',
                    'lastfm_id': 1,
                    'echonest_id': None,
        }
        quality = importer._get_quality(metadata) 
        self.assertEquals(quality, 101)
        
        metadata = {'bitrate': '192',
                    'lastfm_id': None,
                    'echonest_id': 1,
        }
        quality = importer._get_quality(metadata) 
        self.assertEquals(quality, 101)

        metadata = {'bitrate': '192',
                    'lastfm_id': 1,
                    'echonest_id': 1,
        }
        quality = importer._get_quality(metadata) 
        self.assertEquals(quality, 102)
        
    def test_generate_path(self):
        import os
        importer = SongImporter()
        filename, path = importer._generate_filename_and_path_for_song()
        self.assertEquals(len(filename), len('123456789.mp3'))
        
        preview_path = importer._get_filepath_for_preview(path)
        self.assertTrue(preview_path.find("preview64") > -1)
        self.assertEquals(len(os.path.basename(preview_path)), len('789_preview64.mp3'))
        
    def test_create_song_instance(self):
        radio = Radio.objects.radio_for_user(self.user)
        
        importer = SongImporter()
        song_instance = importer._create_song_instance(None, None)
        self.assertEquals(song_instance, None)
        
        sm = SongMetadata(name='name',
                          album_name='album',
                          artist_name='artist')
        sm.save()
        infos = {
            'radio_id': radio.id
        }
        si = importer._create_song_instance(sm, infos)
        self.assertEquals(si.metadata, sm)
        self.assertEquals(si.playlist.radio, radio)
        
        self.assertFalse(radio.ready)

    def test_create_song_instance_ready_attribute(self):
        radio = Radio.objects.radio_for_user(self.user)
        importer = SongImporter()
        song_instance = importer._create_song_instance(None, None)
        self.assertEquals(song_instance, None)
        
        sm = SongMetadata(name='name',
                          album_name='album',
                          artist_name='artist',
                          yasound_song_id=42)
        sm.save()
        infos = {
            'radio_id': radio.id
        }
        si = importer._create_song_instance(sm, infos)
        self.assertEquals(si.metadata, sm)
        self.assertEquals(si.playlist.radio, radio)
        
        radio = Radio.objects.radio_for_user(self.user)
        self.assertTrue(radio.ready)
        
    def test_generate_filename(self):
        filename = generate_default_filename(None)
        self.assertEquals(len(filename), len('2012-03-12-16:06'))

        radio = Radio.objects.radio_for_user(self.user)
        filename = generate_default_filename({'radio_id': radio.id})
        self.assertEquals(len(filename), len('test-2012-03-12-16:06'))

        profile = self.user.get_profile()
        profile.name = 'my-beloved-name'
        profile.save()

        filename = generate_default_filename({'radio_id': radio.id})
        self.assertEquals(len(filename), len('my-beloved-name-2012-03-12-16:06'))

        profile.delete()

        filename = generate_default_filename({'radio_id': radio.id})
        self.assertEquals(len(filename), len('test-2012-03-12-16:06'))
        
    def test_import_without_metadata_in_file(self):
        importer = SongImporter()
        binary = File(open('./apps/yabase/fixtures/mp3/without_metadata.mp3'))
        sm, _message = importer.import_song(binary, metadata=None, convert=False, allow_unknown_song=False)
        self.assertIsNone(sm)
    
    def test_import_without_metadata_in_file_and_with_given_metadata(self):
        importer = SongImporter()
        binary = File(open('./apps/yabase/fixtures/mp3/without_metadata.mp3'))
        
        metadata = {
            'title': 'my mp3',
            'artist': 'my artist',
            'album': 'my album',
        }
        sm, _message = importer.import_song(binary, metadata=metadata, convert=False, allow_unknown_song=False)
        
        self.assertIsNotNone(sm.yasound_song_id)
        self.assertEquals(sm.name, 'my mp3')
        self.assertEquals(sm.artist_name, 'my artist')
        self.assertEquals(sm.album_name, 'my album')
        
    def test_import_same_song(self):
        importer = SongImporter()
        binary = File(open('./apps/yabase/fixtures/mp3/without_metadata.mp3'))
        
        metadata = {
            'title': 'my mp3',
            'artist': 'my artist',
            'album': 'my album',
        }
        sm, _message = importer.import_song(binary, metadata=metadata, convert=False, allow_unknown_song=False)
        
        self.assertIsNotNone(sm.yasound_song_id)
        self.assertEquals(sm.name, 'my mp3')
        self.assertEquals(sm.artist_name, 'my artist')
        self.assertEquals(sm.album_name, 'my album')

        yasound_song = YasoundSong.objects.get(id=sm.yasound_song_id)
        self.assertEquals(yasound_song.name, 'my mp3')
        
        sm2, _message = importer.import_song(binary, metadata=metadata, convert=False, allow_unknown_song=False)
        self.assertEquals(sm2, sm)

    def test_import_same_song_with_different_name(self):
        importer = SongImporter()
        binary = File(open('./apps/yabase/fixtures/mp3/without_metadata.mp3'))
        
        metadata = {
            'title': 'my mp3',
            'artist': 'my artist',
            'album': 'my album',
        }
        sm, _message = importer.import_song(binary, metadata=metadata, convert=False, allow_unknown_song=False)
        
        self.assertIsNotNone(sm.yasound_song_id)
        self.assertEquals(sm.name, 'my mp3')
        self.assertEquals(sm.artist_name, 'my artist')
        self.assertEquals(sm.album_name, 'my album')

        yasound_song = YasoundSong.objects.get(id=sm.yasound_song_id)
        self.assertEquals(yasound_song.name, 'my mp3')
        
        metadata = {
            'title': 'my other mp3',
            'artist': 'my other artist',
            'album': 'my other album',
        }
        sm, _message = importer.import_song(binary, metadata=metadata, convert=False, allow_unknown_song=False)
        self.assertEquals(sm.yasound_song_id, yasound_song.id)
        self.assertEquals(sm.name, 'my other mp3')
        self.assertEquals(sm.artist_name, 'my other artist')
        self.assertEquals(sm.album_name, 'my other album')
        
        yasound_song = YasoundSong.objects.get(id=sm.yasound_song_id)
        self.assertEquals(yasound_song.name, 'my mp3')

class TestRadioDeleted(TestCase):
    def setUp(self):
        erase_index()
        user = User(email="test@yasound.com", username="test", is_superuser=False, is_staff=False)
        user.set_password('test')
        user.save()
        self.client.login(username="test", password="test")
        self.user = user   
    
    def test_remove_song_instance(self):
        radio = Radio.objects.radio_for_user(self.user)
        radio_id = radio.id
        
        playlist = generate_playlist(song_count=100)
        playlist.radio = radio
        playlist.save()
        
        self.assertEquals(SongInstance.objects.all().count(), 100)
        radio.delete_song_instances([1])
        self.assertEquals(SongInstance.objects.all().count(), 100-1)
        
        si = SongInstance.objects.get(id=2)
        ns = NextSong(radio=radio, song=si, order=1)
        ns.save()


        radio.delete_song_instances([2,3,4])
        self.assertEquals(SongInstance.objects.all().count(), 100-4)

        radio = Radio.objects.get(id=radio_id)
        radio.current_song = SongInstance.objects.get(id=5)
        radio.save()
        self.assertEquals(SongInstance.objects.all().count(), 100-4)

        radio.delete_song_instances([5])
        self.assertEquals(SongInstance.objects.all().count(), 100-5)

        # check that radio is still here
        radio = Radio.objects.get(id=radio_id)
     
    def test_fuzzy_index(self):
        results = Radio.objects.search_fuzzy('test')
        self.assertEquals(len(results), 1)
        
        results = Radio.objects.search_fuzzy('rienrienrien')
        self.assertEquals(len(results), 0)
        
    def test_fuzzy_index_deleted(self):
        results = Radio.objects.search_fuzzy('uneradio')
        self.assertEquals(len(results), 0)

        radio = Radio(name='uneradio')
        radio.save()
        
        results = Radio.objects.search_fuzzy('uneradio')
        self.assertEquals(len(results), 1)

        results = Radio.objects.search_fuzzy('test')
        self.assertEquals(len(results), 1)
        
        Radio.objects.radio_for_user(self.user).delete()

        results = Radio.objects.search_fuzzy('test')
        self.assertEquals(len(results), 0)
                