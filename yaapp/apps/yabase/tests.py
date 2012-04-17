from django.contrib.auth.models import User
from django.core.files import File
from django.core.urlresolvers import reverse
from django.db.models.aggregates import Count
from django.db.models.fields import FieldDoesNotExist
from django.test import TestCase
from models import NextSong, SongInstance, RADIO_NEXT_SONGS_COUNT, Radio, \
    RadioUser
from task import process_playlists_exec
from tastypie.models import ApiKey
from tests_utils import generate_playlist
from yabase.import_utils import SongImporter, generate_default_filename
from yabase.models import FeaturedContent, Playlist, SongMetadata
from yaref import test_utils as yaref_test_utils
from yaref.models import YasoundAlbum, YasoundSong, YasoundArtist
from yasearch.indexer import erase_index, add_song
import import_utils
import os
import settings as yabase_settings
import simplejson as json
import utils as yabase_utils

class TestMiddleware(TestCase):
    def setUp(self):
        user = User(email="test@yasound.com", username="test", is_superuser=True, is_staff=True)
        user.set_password('test')
        user.save()
        self.client.login(username="test", password="test")
        self.user = user        
    
    def test_slashes(self):
        self.client.get('/status//')
        res = self.client.post('/status//', {'username': 'john', 'password': 'smith'})
        print res
        
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
   
    def test_atomic_inc(self):
        radio = self.radio
        yabase_utils.atomic_inc(radio, 'overall_listening_time', 1000)

        radio2 = Radio()
        radio2.save()
        yabase_utils.atomic_inc(radio2, 'overall_listening_time', 3000)
        
        self.assertEquals(Radio.objects.get(id=radio.id).overall_listening_time, 1000)
        self.assertEquals(Radio.objects.get(id=radio2.id).overall_listening_time, 3000)
       
        yabase_utils.atomic_inc(radio, 'overall_listening_time', -1000)
        self.assertEquals(Radio.objects.get(id=radio.id).overall_listening_time, 0)

        self.assertRaises(FieldDoesNotExist,yabase_utils.atomic_inc, radio, 'overall_listening_time1', -1000)
            
   
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
        
class TestFuzzySong(TestCase):
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

class TestFuzzyRadio(TestCase):
    def setUp(self):
        erase_index()
        user = User(email="test@yasound.com", username="test", is_superuser=False, is_staff=False)
        user.set_password('test')
        user.save()
        self.client.login(username="test", password="test")
        self.user = user        
            
    def test_search(self):
        self.assertEquals(len(Radio.objects.search_fuzzy("pizza")), 0)
        
        Radio(name='pizza', ready=True, creator=self.user).save()
        Radio(name='velo', ready=True, creator=self.user).save()
        Radio(name='maison', ready=True, creator=self.user).save()

        self.assertEquals(len(Radio.objects.search_fuzzy("pizza")), 1)
        self.assertEquals(len(Radio.objects.search_fuzzy("velo")), 1)
        self.assertEquals(len(Radio.objects.search_fuzzy("maison")), 1)

        radio = Radio.objects.get(name='pizza')
        radio.save()
        self.assertEquals(len(Radio.objects.search_fuzzy("pizza")), 1)
        radio.name = 'cucarracha'
        radio.save()
        self.assertEquals(len(Radio.objects.search_fuzzy("pizza")), 0)
        self.assertEquals(len(Radio.objects.search_fuzzy("cucarracha")), 1)
        
        radio.name = 'pizza'
        radio.save()
        self.assertEquals(len(Radio.objects.search_fuzzy("pizza")), 1)
        self.assertEquals(len(Radio.objects.search_fuzzy("cucarracha")), 0)

        from yasearch import models as yasearch_models
        yasearch_models.build_mongodb_index()
        
        self.assertEquals(len(Radio.objects.search_fuzzy("pizza")), 1)
        self.assertEquals(len(Radio.objects.search_fuzzy("velo")), 1)
        self.assertEquals(len(Radio.objects.search_fuzzy("maison")), 1)

        erase_index()

        self.assertEquals(len(Radio.objects.search_fuzzy("pizza")), 0)
        self.assertEquals(len(Radio.objects.search_fuzzy("velo")), 0)
        self.assertEquals(len(Radio.objects.search_fuzzy("maison")), 0)

        yasearch_models.build_mongodb_index()
        
        self.assertEquals(len(Radio.objects.search_fuzzy("pizza")), 1)
        self.assertEquals(len(Radio.objects.search_fuzzy("velo")), 1)
        self.assertEquals(len(Radio.objects.search_fuzzy("maison")), 1)

        
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
        
        # all songs are enabled
        self.assertEquals(SongInstance.objects.filter(enabled=True).count(), 492)
        
        
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

class TestImportCover(TestCase):
    def setUp(self):
        user = User(email="test@yasound.com", username="test", is_superuser=False, is_staff=False)
        user.set_password('test')
        user.save()
        self.client.login(username="test", password="test")
        self.user = user     
        
        try:
            os.remove('./apps/yabase/fixtures/artwork/d.mp3')
        except:
            pass
        
        YasoundSong.objects.all().delete()
        erase_index()   

    def test_mp3_without_cover(self):
        importer = SongImporter()
        data, extension = importer.find_song_cover_data('./apps/yabase/fixtures/artwork/without_cover.mp3')
        self.assertIsNone(data)
        self.assertIsNone(extension)
        
    def test_mp3_with_cover(self):
        importer = SongImporter()
        data, extension = importer.find_song_cover_data('./apps/yabase/fixtures/artwork/with_cover.mp3')
        self.assertIsNotNone(data)
        self.assertEquals(extension, '.jpg')

    def test_mp3_with_cover2(self):
        importer = SongImporter()
        data, extension = importer.find_song_cover_data('./apps/yabase/fixtures/artwork/with_cover2.mp3')
        self.assertIsNotNone(data)
        self.assertEquals(extension, '.png')

    def test_m4a_without_cover(self):
        importer = SongImporter()
        data, extension = importer.find_song_cover_data('./apps/yabase/fixtures/artwork/without_cover.m4a')
        self.assertIsNone(data)
        self.assertIsNone(extension)
        
    def test_m4a_with_cover(self):
        importer = SongImporter()
        data, extension = importer.find_song_cover_data('./apps/yabase/fixtures/artwork/with_cover.m4a')
        self.assertIsNotNone(data)
        self.assertEquals(extension, '.png')

    def test_full_m4a_with_cover(self):
        filepath = './apps/yabase/fixtures/artwork/with_cover.m4a'
        sm, _message = import_utils.import_song(filepath, metadata=None, convert=True, allow_unknown_song=False)
        self.assertIsNotNone(sm)
        yasound_song_id = sm.yasound_song_id
        song = YasoundSong.objects.get(id=yasound_song_id)
        self.assertIsNotNone(song.cover_filename)

    def test_full_m4a_without_cover(self):
        filepath = './apps/yabase/fixtures/artwork/without_cover.m4a'
        sm, _message = import_utils.import_song(filepath, metadata=None, convert=True, allow_unknown_song=False)
        self.assertIsNotNone(sm)
        yasound_song_id = sm.yasound_song_id
        song = YasoundSong.objects.get(id=yasound_song_id)
        self.assertIsNone(song.cover_filename)
        
    def test_full_mp3_with_cover(self):
        filepath = './apps/yabase/fixtures/artwork/with_cover.mp3'
        sm, _message = import_utils.import_song(filepath, metadata=None, convert=True, allow_unknown_song=False)
        self.assertIsNotNone(sm)
        yasound_song_id = sm.yasound_song_id
        song = YasoundSong.objects.get(id=yasound_song_id)
        self.assertIsNotNone(song.cover_filename)

    def test_full_mp3_without_cover(self):
        filepath = './apps/yabase/fixtures/artwork/without_cover.mp3'
        sm, _message = import_utils.import_song(filepath, metadata=None, convert=True, allow_unknown_song=False)
        self.assertIsNotNone(sm)
        yasound_song_id = sm.yasound_song_id
        song = YasoundSong.objects.get(id=yasound_song_id)
        self.assertIsNone(song.cover_filename)
        
class TestImport(TestCase):
    def setUp(self):
        user = User(email="test@yasound.com", username="test", is_superuser=False, is_staff=False)
        user.set_password('test')
        user.save()
        self.client.login(username="test", password="test")
        self.user = user   
        
        try:  
            os.remove('./apps/yabase/fixtures/mp3/d.mp3')
        except:
            pass
        
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
        filepath = './apps/yabase/fixtures/mp3/without_metadata.mp3'
        sm, _message = importer.import_song(filepath, metadata=None, convert=False, allow_unknown_song=False)
        self.assertIsNone(sm)
    
    def test_import_without_metadata_in_file_and_with_given_metadata(self):
        importer = SongImporter()
        filepath = './apps/yabase/fixtures/mp3/without_metadata.mp3'
        
        metadata = {
            'title': 'my mp3',
            'artist': 'my artist',
            'album': 'my album',
        }
        sm, _message = importer.import_song(filepath, metadata=metadata, convert=False, allow_unknown_song=False)
        
        self.assertIsNotNone(sm.yasound_song_id)
        self.assertEquals(sm.name, 'my mp3')
        self.assertEquals(sm.artist_name, 'my artist')
        self.assertEquals(sm.album_name, 'my album')
        
    def test_import_without_metadata_in_file_and_with_given_metadata_and_radio(self):
        radio = Radio.objects.radio_for_user(self.user)
        importer = SongImporter()
        filepath = './apps/yabase/fixtures/mp3/without_metadata.mp3'
        
        metadata = {
            'title': 'my mp3',
            'artist': 'my artist',
            'album': 'my album',
            'radio_id': '1',
        }
        sm, _message = importer.import_song(filepath, metadata=metadata, convert=False, allow_unknown_song=False)
        
        self.assertIsNotNone(sm.yasound_song_id)
        self.assertEquals(sm.name, 'my mp3')
        self.assertEquals(sm.artist_name, 'my artist')
        self.assertEquals(sm.album_name, 'my album')
        
        si = SongInstance.objects.get(id=1)
        self.assertEquals(si.playlist.radio, radio)
        self.assertEquals(si.metadata, sm)
        self.assertTrue(si.enabled)
        
        
    def test_import_same_song(self):
        importer = SongImporter()
        filepath = './apps/yabase/fixtures/mp3/without_metadata.mp3'
        
        metadata = {
            'title': 'my mp3',
            'artist': 'my artist',
            'album': 'my album',
        }
        sm, _message = importer.import_song(filepath, metadata=metadata, convert=False, allow_unknown_song=False)
        
        self.assertIsNotNone(sm.yasound_song_id)
        self.assertEquals(sm.name, 'my mp3')
        self.assertEquals(sm.artist_name, 'my artist')
        self.assertEquals(sm.album_name, 'my album')

        yasound_song = YasoundSong.objects.get(id=sm.yasound_song_id)
        self.assertEquals(yasound_song.name, 'my mp3')
        
        sm2, _message = importer.import_song(filepath, metadata=metadata, convert=False, allow_unknown_song=False)
        self.assertEquals(sm2, sm)

    def test_import_with_duplicated_metatadas(self):
        importer = SongImporter()
        filepath = './apps/yabase/fixtures/mp3/without_metadata.mp3'
        
        for _i in range(0, 10):
            SongMetadata(name='my mp3',
                          artist_name='my artist',
                          album_name='my album').save()

        metadata = {
            'title': 'my mp3',
            'artist': 'my artist',
            'album': 'my album',
        }
        sm, _message = importer.import_song(filepath, metadata=metadata, convert=False, allow_unknown_song=False)
        
        self.assertIsNotNone(sm.yasound_song_id)
        self.assertEquals(sm.name, 'my mp3')
        self.assertEquals(sm.artist_name, 'my artist')
        self.assertEquals(sm.album_name, 'my album')


    def test_import_same_song_with_different_name(self):
        importer = SongImporter()
        filepath = './apps/yabase/fixtures/mp3/without_metadata.mp3'
        
        metadata = {
            'title': 'my mp3',
            'artist': 'my artist',
            'album': 'my album',
        }
        sm, _message = importer.import_song(filepath, metadata=metadata, convert=False, allow_unknown_song=False)
        
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
        sm, _message = importer.import_song(filepath, metadata=metadata, convert=False, allow_unknown_song=False)
        self.assertEquals(sm.yasound_song_id, yasound_song.id)
        self.assertEquals(sm.name, 'my other mp3')
        self.assertEquals(sm.artist_name, 'my other artist')
        self.assertEquals(sm.album_name, 'my other album')
        
        yasound_song = YasoundSong.objects.get(id=sm.yasound_song_id)
        self.assertEquals(yasound_song.name, 'my mp3')

    def test_import_owner_id_is_none(self):
        importer = SongImporter()
        filepath = './apps/yabase/fixtures/mp3/without_metadata.mp3'
        
        metadata = {
            'title': 'my mp3',
            'artist': 'my artist',
            'album': 'my album',
        }
        sm, _message = importer.import_song(filepath, metadata=metadata, convert=False, allow_unknown_song=False)
        self.assertIsNotNone(sm.yasound_song_id)
        yasound_song = YasoundSong.objects.get(id=sm.yasound_song_id)
        self.assertIsNone(yasound_song.owner_id)

    def test_import_owner_id_is_not_none(self):
        importer = SongImporter()
        filepath = './apps/yabase/fixtures/mp3/unknown.mp3'
        radio = Radio.objects.radio_for_user(self.user)
        
        metadata = {
            'title': 'my own mp3',
            'artist': 'my artist',
            'album': 'my album',
            'radio_id':  radio.id
        }
        sm, _message = importer.import_song(filepath, metadata=metadata, convert=False, allow_unknown_song=True)
        self.assertIsNotNone(sm.yasound_song_id)
        yasound_song = YasoundSong.objects.get(id=sm.yasound_song_id)
        self.assertEquals(yasound_song.owner_id, self.user.id)

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
                
    def test_duplicates(self):
        radio = Radio(name='uneradio')
        radio.save()
        
        results = Radio.objects.search_fuzzy('uneradio')
        self.assertEquals(len(results), 1)

        radio.save()

        results = Radio.objects.search_fuzzy('uneradio')
        self.assertEquals(len(results), 1)

        radio.name = 'toto'
        radio.save()
        
        results = Radio.objects.search_fuzzy('uneradio')
        self.assertEquals(len(results), 0)

        results = Radio.objects.search_fuzzy('toto')
        self.assertEquals(len(results), 1)
        
class TestApi(TestCase):
    def setUp(self):
        erase_index()
        user = User(email="test@yasound.com", username="test", is_superuser=True, is_staff=True)
        user.set_password('test')
        user.save()
        self.client.login(username="test", password="test")
        self.user = user 
        self.key = ApiKey.objects.get(user=self.user).key
        self.username = self.user.username       
        
    def testTopLimitation(self):
        for i in range(0, 100):
            Radio(name='%d' % (i), ready=True, creator=self.user).save()
        url = reverse('api_dispatch_list', kwargs={'resource_name': 'top_radio', 'api_name': 'v1',})
        res = self.client.get(url,{'api_key': self.key, 'username': self.username})
        self.assertEquals(res.status_code, 200)

        data = res.content
        decoded_data = json.loads(data)
        meta = decoded_data['meta']
        self.assertEquals(meta['total_count'], yabase_settings.TOP_RADIOS_LIMIT)
        