# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.core.files import File
from django.conf import settings
from django.core.urlresolvers import reverse
from django.db.models.aggregates import Count
from django.db.models.fields import FieldDoesNotExist
from django.test import TestCase
from mock import Mock, patch
from models import NextSong, SongInstance, RADIO_NEXT_SONGS_COUNT, Radio, \
    RadioUser, Announcement
from task import process_playlists_exec
from tastypie.models import ApiKey
from tests_utils import generate_playlist
from yabase.import_utils import SongImporter, generate_default_filename, \
    parse_itunes_line, import_song
from yabase.models import FeaturedContent, Playlist, SongMetadata, WallEvent
from yabase.task import process_playlists
from yacore.database import atomic_inc
from yacore.tags import clean_tags
from yaref import test_utils as yaref_test_utils
from yaref.models import YasoundAlbum, YasoundSong, YasoundArtist
from yasearch.indexer import erase_index, add_song
from yasearch.models import MostPopularSongsManager
import import_utils
import os
import settings as yabase_settings
import simplejson as json
from django.test.client import RequestFactory
from task import fast_import, delete_radios_definitively
import datetime
import uploader
from yahistory.models import ProgrammingHistory

def turn_off_auto_now(Clazz, field_name):
    def auto_now_off(field):
        field.auto_now = False
    iter_fields_and_do(Clazz, field_name, auto_now_off)

def turn_on_auto_now(Clazz, field_name):
    def auto_now_off(field):
        field.auto_now = True
    iter_fields_and_do(Clazz, field_name, auto_now_off)

def turn_off_auto_now_add(Clazz, field_name):
    def auto_now_add_off(field):
        field.auto_now_add = False
    iter_fields_and_do(Clazz, field_name, auto_now_add_off)

def turn_on_auto_now_add(Clazz, field_name):
    def auto_now_add_off(field):
        field.auto_now_add = True
    iter_fields_and_do(Clazz, field_name, auto_now_add_off)

def iter_fields_and_do(Clazz, field_name, func):
    for field in Clazz._meta.local_fields:
        if field.name == field_name:
            func(field)


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


class TestMisc(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_push_url(self):
        from views import WebAppView
        wa = WebAppView()
        request = self.factory.get('/status/')
        request.META['HTTP_HOST'] = 'localhost:8000'
        url = wa._get_push_url(request)

        good_url = '%s://%s:%d/' % (settings.DEFAULT_HTTP_PROTOCOL, 'localhost', settings.YASOUND_PUSH_PORT)
        self.assertEquals(url, good_url)

        request.META['HTTP_HOST'] = 'localhost'
        url = wa._get_push_url(request)

        good_url = '%s://%s:%d/' % (settings.DEFAULT_HTTP_PROTOCOL, 'localhost', settings.YASOUND_PUSH_PORT)
        self.assertEquals(url, good_url)


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
        atomic_inc(radio, 'overall_listening_time', 1000)

        radio2 = Radio()
        radio2.save()
        atomic_inc(radio2, 'overall_listening_time', 3000)

        self.assertEquals(radio.overall_listening_time, 1000)
        self.assertEquals(radio2.overall_listening_time, 3000)

        self.assertEquals(Radio.objects.get(id=radio.id).overall_listening_time, 1000)
        self.assertEquals(Radio.objects.get(id=radio2.id).overall_listening_time, 3000)

        atomic_inc(radio, 'overall_listening_time', -1000)
        self.assertEquals(radio.overall_listening_time, 0)

        self.assertEquals(Radio.objects.get(id=radio.id).overall_listening_time, 0)
        self.assertRaises(FieldDoesNotExist, atomic_inc, radio, 'overall_listening_time1', -1000)

    def test_web_url(self):
        radio = self.radio
        url = radio.web_url
        self.assertEquals(url, 'http://localhost:8000/listen/' + radio.uuid)

    def test_md5(self):
        name = 'name'
        artist = 'artist'
        album = 'album'
        s = SongMetadata(name=name, artist_name=artist, album_name=album)
        self.assertEquals(s.calculate_hash_name(), 'e1c0b58dcdb486247329be94a4b8eee4')

    def test_is_favorite(self):
        radio = self.radio
        user = self.user
        RadioUser.objects.all().delete()

        self.assertFalse(radio.is_favorite(user))

        ru = RadioUser.objects.create(radio=radio, user=user)
        self.assertFalse(radio.is_favorite(user))

        ru.favorite=True
        ru.save()
        self.assertTrue(radio.is_favorite(user))

    def test_deleted(self):
        radio = self.radio
        user = self.user

        self.assertIsNotNone(user.get_profile().own_radio)

        radio.mark_as_deleted()
        radio.save()
        self.assertIsNone(user.get_profile().own_radio)

        delete_radios_definitively()

        self.assertEquals(Radio.objects.all().count(), 1)

        today = datetime.datetime.today()
        past_date = today - datetime.timedelta(days=settings.RADIO_DELETE_DAYS+1)

        turn_off_auto_now(Radio, "updated")

        radio.updated = past_date
        radio.save()

        turn_on_auto_now(Radio, "updated")

        self.assertEquals(Radio.objects.all().count(), 1)

        delete_radios_definitively()

        self.assertEquals(Radio.objects.all().count(), 1) # we do not delete radios right now

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
        redis = Mock(name='redis')
        redis.publish = Mock()

        with patch('yabase.push.Redis') as mock_redis:
            mock_redis.return_value = redis

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
        self.assertEquals(featured_content1.ftype, yabase_settings.FEATURED_SELECTION)

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


        # another featured content but with other type,
        # does not update activated field on other featured contents
        featured_content3 = FeaturedContent(name='featured_2',
                                            activated=True,
                                            ftype=yabase_settings.FEATURED_HOMEPAGE)
        featured_content3.save()

        self.assertEquals(featured_content1.activated, True)
        self.assertEquals(featured_content2.activated, False)
        self.assertEquals(featured_content3.activated, True)

class TestAnnouncementModels(TestCase):
    multi_db = True
    def setUp(self):
        user = User(email="test@yasound.com", username="test", is_superuser=False, is_staff=False)
        user.set_password('test')
        user.save()
        self.client.login(username="test", password="test")
        self.user = user


    def testActivate(self):
        an1 = Announcement.objects.create(name_en='name')
        self.assertEquals(an1.activated, False)
        an1.activated = True
        an1.save()
        self.assertEquals(an1.activated, True)

        an2 = Announcement.objects.create(name_en='name')
        self.assertEquals(an2.activated, False)

        an2.activated = True
        an2.save()
        an1 = Announcement.objects.get(id=an1.id)
        self.assertEquals(an1.activated, False)


class TestImportPlaylist(TestCase):
    def setUp(self):
        user = User(email="test@yasound.com", username="test", is_superuser=False, is_staff=False)
        user.set_password('test')
        user.save()
        Radio.objects.create(creator=user)
        self.client.login(username="test", password="test")
        self.user = user
        erase_index()
        pm = ProgrammingHistory()
        pm.erase_metrics()

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

        pm = ProgrammingHistory()
        event = list(pm.events_for_radio(radio))[0]
        self.assertEquals(pm.details_for_event(event).count(), 643)

        details_success = pm.details_for_event(event, status=ProgrammingHistory.STATUS_SUCCESS)
        self.assertEquals(details_success.count(), 0)

        details_failed = pm.details_for_event(event, status=ProgrammingHistory.STATUS_FAILED)
        self.assertEquals(details_failed.count(), 643)


    def test_import_ok_with_references(self):
        pm = ProgrammingHistory()
        radio = Radio.objects.radio_for_user(self.user)
        self.assertEquals(pm.events_for_radio(radio).count(), 0)

        f = open('./apps/yabase/fixtures/playlist.data')
        content_compressed = f.read()
        f.close()

        song = yaref_test_utils.generate_yasound_song('one of a kind', 'meds', 'placebo')
        add_song(song)
        self.assertEquals(SongInstance.objects.all().count(), 0)
        process_playlists_exec(radio, content_compressed=content_compressed)
        self.assertEquals(SongInstance.objects.all().count(), 492)
        self.assertEquals(SongMetadata.objects.filter(yasound_song_id__isnull=True).count(), 491)

        self.assertEquals(pm.events_for_radio(radio).count(), 1)

        event = list(pm.events_for_radio(radio))[0]
        self.assertEquals(pm.details_for_event(event).count(), 643)

        details_success = pm.details_for_event(event, status=ProgrammingHistory.STATUS_SUCCESS)
        self.assertEquals(details_success.count(), 1)

        details_failed = pm.details_for_event(event, status=ProgrammingHistory.STATUS_FAILED)
        self.assertEquals(details_failed.count(), 642)

    def test_fast_import(self):
        mm = MostPopularSongsManager()
        mm.drop()

        self.user.is_superuser = True
        self.user.save()
        self.client.login(username="test", password="test")

        song = yaref_test_utils.generate_yasound_song('one of a kind', 'meds', 'placebo')
        add_song(song)

        self.assertEquals(SongInstance.objects.all().count(), 0)

        radio = Radio.objects.radio_for_user(self.user)
        f = open('./apps/yabase/fixtures/playlist.data')
        content_compressed = f.read()
        f.close()

        process_playlists_exec(radio, content_compressed=content_compressed)

        self.assertEquals(SongInstance.objects.all().count(), 492)
        self.assertEquals(SongMetadata.objects.filter(yasound_song_id__isnull=True).count(), 491)

        # all songs are enabled
        self.assertEquals(SongInstance.objects.filter(enabled=True).count(), 492)

        doc = mm.find(name='one of a kind', artist='placebo', album='meds')
        self.assertEquals(doc.get('yasound_song_id'), song.id)

        self.user.is_superuser = False
        self.user.save()
        self.client.login(username="test", password="test")

        found, _notfound = process_playlists_exec(radio, content_compressed=content_compressed)
        self.assertEquals(found, 1)

    def test_fast_import_with_different_metadata(self):
        mm = MostPopularSongsManager()
        mm.drop()

        self.user.is_superuser = True
        self.user.save()
        self.client.login(username="test", password="test")

        song = yaref_test_utils.generate_yasound_song('one of a kind', 'meds classical version', 'placebo')
        add_song(song)

        radio = Radio.objects.radio_for_user(self.user)
        playlist, _created = radio.get_or_create_default_playlist()

        song_instance = import_utils.import_from_string('one of a kind', 'meds classical version', 'placebo', playlist)

        mp = MostPopularSongsManager()
        mp.add_song(song_instance)

        si = fast_import('one of a kind', 'meds classical version', 'placebo', playlist)
        self.assertEquals(si.metadata.id, song_instance.metadata.id)

        si2 = fast_import('one of a kind', 'meds', 'placebo', playlist)
        self.assertNotEquals(si2.metadata.id, song_instance.metadata.id)
        self.assertEquals(si2.metadata.yasound_song_id, song_instance.metadata.yasound_song_id)

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
        Radio.objects.create(creator=user)

        try:
            os.remove('./apps/yabase/fixtures/mp3/d.mp3')
        except:
            pass

        YasoundSong.objects.all().delete()
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
        importer = SongImporter()
        filename, _path = importer._generate_filename_and_path_for_song()
        self.assertEquals(len(filename), len('123456789.mp3'))

        yasound_song = YasoundSong(filename=filename)
        preview_path = yasound_song.get_filepath_for_preview()
        self.assertTrue(preview_path.find("preview64") > -1)
        self.assertEquals(len(os.path.basename(preview_path)), len('789_preview64.mp3'))

        lq_path = yasound_song.get_filepath_for_lq()
        self.assertTrue(lq_path.find("lq") > -1)
        self.assertEquals(len(os.path.basename(lq_path)), len('789_lq.mp3'))

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
        filepath = './apps/yabase/fixtures/mp3/without_metadata.mp3'
        sm, _message = import_song(filepath, metadata=None, convert=False, allow_unknown_song=False)
        self.assertIsNone(sm)

    def test_import_without_metadata_in_file_and_with_given_metadata(self):
        filepath = './apps/yabase/fixtures/mp3/without_metadata.mp3'

        metadata = {
            'title': 'my mp3',
            'artist': 'my artist',
            'album': 'my album',
        }
        sm, _message = import_song(filepath, metadata=metadata, convert=False, allow_unknown_song=True)

        self.assertIsNotNone(sm.yasound_song_id)
        self.assertEquals(sm.name, 'my mp3')
        self.assertEquals(sm.artist_name, 'my artist')
        self.assertEquals(sm.album_name, 'my album')

        yasound_song = YasoundSong.objects.get(id=sm.yasound_song_id)
        path = yasound_song.get_song_path()
        preview_path = yasound_song.get_song_preview_path()
        lq_path = yasound_song.get_song_lq_path()

        self.assertTrue(os.path.isfile(path))
        self.assertFalse(os.path.isfile(preview_path))
        self.assertTrue(os.path.isfile(lq_path))

    def test_import_without_metadata_in_file_and_with_given_metadata_and_radio(self):
        radio = Radio.objects.radio_for_user(self.user)
        filepath = './apps/yabase/fixtures/mp3/without_metadata.mp3'

        metadata = {
            'title': 'my mp3',
            'artist': 'my artist',
            'album': 'my album',
            'radio_id': '1',
        }
        sm, _message = import_song(filepath, metadata=metadata, convert=False, allow_unknown_song=True)

        self.assertIsNotNone(sm.yasound_song_id)
        self.assertEquals(sm.name, 'my mp3')
        self.assertEquals(sm.artist_name, 'my artist')
        self.assertEquals(sm.album_name, 'my album')

        si = SongInstance.objects.get(id=1)
        self.assertEquals(si.playlist.radio, radio)
        self.assertEquals(si.metadata, sm)
        self.assertTrue(si.enabled)

    def test_import_without_metadata_in_file_and_with_given_metadata_and_radio_uuid(self):
        radio = Radio.objects.radio_for_user(self.user)
        filepath = './apps/yabase/fixtures/mp3/without_metadata.mp3'

        metadata = {
            'title': 'my mp3',
            'artist': 'my artist',
            'album': 'my album',
            'radio_uuid': radio.uuid,
        }
        sm, _message = import_song(filepath, metadata=metadata, convert=False, allow_unknown_song=True)

        self.assertIsNotNone(sm.yasound_song_id)
        self.assertEquals(sm.name, 'my mp3')
        self.assertEquals(sm.artist_name, 'my artist')
        self.assertEquals(sm.album_name, 'my album')

        si = SongInstance.objects.get(id=1)
        self.assertEquals(si.playlist.radio, radio)
        self.assertEquals(si.metadata, sm)
        self.assertTrue(si.enabled)

    def test_import_same_song(self):
        filepath = './apps/yabase/fixtures/mp3/known_by_echonest_lastfm.mp3'

        metadata = {
            'title': 'my mp3',
            'artist': 'my artist',
            'album': 'my album',
        }
        sm, _message = import_song(filepath, metadata=metadata, convert=False, allow_unknown_song=True)

        self.assertIsNotNone(sm.yasound_song_id)
        self.assertEquals(sm.name, 'my mp3')
        self.assertEquals(sm.artist_name, 'my artist')
        self.assertEquals(sm.album_name, 'my album')
        self.assertEqual(sm.hash_name, "8ea373e35831fa28dfedbe77b47be7ef")
        yasound_song = YasoundSong.objects.get(id=sm.yasound_song_id)
        self.assertEquals(yasound_song.name, 'my mp3')

        self.assertEquals(yasound_song.musicbrainz_id, '2a124411-41b8-4cbb-984b-6e10878d412b')

        sm2, _message = import_song(filepath, metadata=metadata, convert=False, allow_unknown_song=True)
        self.assertNotEquals(sm2.yasound_song_id, sm.yasound_song_id)

    def test_import_after_missed_import(self):
        filepath = './apps/yabase/fixtures/mp3/known_by_echonest_lastfm.mp3'
        radio = Radio.objects.radio_for_user(self.user)

        metadata = {
            'title': 'my mp3',
            'artist': 'my artist',
            'album': 'my album',
            'radio_id': radio.id
        }
        sm, _message = import_song(filepath, metadata=metadata, convert=False, allow_unknown_song=True)

        self.assertIsNotNone(sm.yasound_song_id)
        self.assertEquals(sm.name, 'my mp3')
        self.assertEquals(sm.artist_name, 'my artist')
        self.assertEquals(sm.album_name, 'my album')
        self.assertEqual(sm.hash_name, "8ea373e35831fa28dfedbe77b47be7ef")

        sm.yasound_song_id = None
        sm.save()

        sm2, _message = import_song(filepath, metadata=metadata, convert=False, allow_unknown_song=True)
        self.assertEquals(sm2.id, sm.id)


    def test_double_import(self):
        filepath = './apps/yabase/fixtures/mp3/known_by_echonest_lastfm.mp3'
        radio = Radio.objects.radio_for_user(self.user)

        metadata = {
            'title': 'my mp3',
            'artist': 'my artist',
            'album': 'my album',
            'radio_id': radio.id
        }
        sm, _message = import_song(filepath, metadata=metadata, convert=False, allow_unknown_song=True)

        self.assertIsNotNone(sm.yasound_song_id)
        self.assertEquals(sm.name, 'my mp3')
        self.assertEquals(sm.artist_name, 'my artist')
        self.assertEquals(sm.album_name, 'my album')
        self.assertEqual(sm.hash_name, "8ea373e35831fa28dfedbe77b47be7ef")

        sm2, _message = import_song(filepath, metadata=metadata, convert=False, allow_unknown_song=True)
        self.assertNotEquals(sm2.id, sm.id)

    def test_import_with_duplicated_metatadas(self):
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
        sm, _message = import_song(filepath, metadata=metadata, convert=False, allow_unknown_song=True)

        self.assertIsNotNone(sm.yasound_song_id)
        self.assertEquals(sm.name, 'my mp3')
        self.assertEquals(sm.artist_name, 'my artist')
        self.assertEquals(sm.album_name, 'my album')


    def test_import_synonyms(self):
        filepath = './apps/yabase/fixtures/mp3/known_by_echonest_lastfm.mp3'

        metadata = {
            'title': 'my mp3',
            'artist': 'my artist',
            'album': 'my album',
        }
        sm, _message = import_song(filepath, metadata=metadata, convert=False, allow_unknown_song=True)

        self.assertIsNotNone(sm.yasound_song_id)
        self.assertEquals(sm.name, 'my mp3')
        self.assertEquals(sm.artist_name, 'my artist')
        self.assertEquals(sm.album_name, 'my album')

        self.assertEquals(SongMetadata.objects.all().count(), 2)

        sm = SongMetadata.objects.get(name='Biscuit')
        self.assertEquals(sm.name, 'Biscuit')
        self.assertEquals(sm.artist_name, 'Portishead')
        self.assertEquals(sm.album_name, 'Dummy')
        self.assertEquals(sm.yasound_song_id, 1)

        sm = SongMetadata.objects.get(name='my mp3')
        self.assertEquals(sm.name, 'my mp3')
        self.assertEquals(sm.artist_name, 'my artist')
        self.assertEquals(sm.album_name, 'my album')
        self.assertEquals(sm.yasound_song_id, 1)


    def test_import_same_song_with_different_name(self):
        filepath = './apps/yabase/fixtures/mp3/known_by_echonest_lastfm.mp3'

        metadata = {
            'title': 'my mp3',
            'artist': 'my artist',
            'album': 'my album',
        }
        sm, _message = import_song(filepath, metadata=metadata, convert=False, allow_unknown_song=True)

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
        sm, _message = import_song(filepath, metadata=metadata, convert=False, allow_unknown_song=True)
        self.assertNotEquals(sm.yasound_song_id, yasound_song.id)
        self.assertEquals(sm.name, 'my other mp3')
        self.assertEquals(sm.artist_name, 'my other artist')
        self.assertEquals(sm.album_name, 'my other album')

        yasound_song = YasoundSong.objects.get(id=sm.yasound_song_id)
        self.assertEquals(yasound_song.name, 'my other mp3')

    def test_import_owner_id_is_none(self):
        filepath = './apps/yabase/fixtures/mp3/without_metadata.mp3'

        metadata = {
            'title': 'my mp3',
            'artist': 'my artist',
            'album': 'my album',
        }
        sm, _message = import_song(filepath, metadata=metadata, convert=False, allow_unknown_song=True)
        self.assertIsNotNone(sm.yasound_song_id)
        yasound_song = YasoundSong.objects.get(id=sm.yasound_song_id)
        self.assertIsNone(yasound_song.owner_id)

    def test_import_owner_id_is_not_none(self):
        filepath = './apps/yabase/fixtures/mp3/unknown.mp3'
        radio = Radio.objects.radio_for_user(self.user)

        metadata = {
            'title': 'my own mp3',
            'artist': 'my artist',
            'album': 'my album',
            'radio_id':  radio.id
        }
        sm, _message = import_song(filepath, metadata=metadata, convert=False, allow_unknown_song=True)
        self.assertIsNotNone(sm.yasound_song_id)
        yasound_song = YasoundSong.objects.get(id=sm.yasound_song_id)
        self.assertEquals(yasound_song.owner_id, self.user.id)

        self.assertTrue(yasound_song.file_exists())

    def test_rank(self):
        importer = SongImporter()
        filepath = './apps/yabase/fixtures/mp3/known_by_echonest_lastfm.mp3'

        metadata = uploader.get_file_infos(filepath)

        sm, _message = importer.import_song(filepath, metadata=metadata, convert=False, allow_unknown_song=True)
        self.assertIsNotNone(sm.yasound_song_id)

        yasound_song = YasoundSong.objects.get(id=sm.yasound_song_id)
        self.assertIsNotNone(yasound_song.lastfm_fingerprint_id)
        self.assertEquals(yasound_song.lastfm_fingerprint_id, '43565867')
        rank = yasound_song.find_lastfm_rank()
        self.assertEquals(rank, 1.0)

    def test_replace(self):
        importer = SongImporter()
        filepath = './apps/yabase/fixtures/mp3/known_by_echonest_lastfm.mp3'

        metadata = uploader.get_file_infos(filepath)

        sm, _message = importer.import_song(filepath, metadata=metadata, convert=False, allow_unknown_song=True)
        self.assertIsNotNone(sm.yasound_song_id)

        yasound_song = YasoundSong.objects.get(id=sm.yasound_song_id)

        yasound_song.replace(filepath, yasound_song.lastfm_fingerprint_id)
        self.assertIsNotNone(yasound_song.lastfm_fingerprint_id)
        self.assertEquals(yasound_song.lastfm_fingerprint_id, '43565867')

        song_path = yasound_song.get_song_path()
        name, extension = os.path.splitext(song_path)
        backup_name = u'%s_quarantine%s' % (name, extension)
        self.assertTrue(os.path.exists(backup_name))

        yasound_song.replace(filepath, yasound_song.lastfm_fingerprint_id)
        backup_name = u'%s_quarantine%s' % (name, extension)
        self.assertTrue(os.path.exists(backup_name))
        backup_name = u'%s_quarantine_1%s' % (name, extension)
        self.assertTrue(os.path.exists(backup_name))

        yasound_song.replace(filepath, yasound_song.lastfm_fingerprint_id)
        backup_name = u'%s_quarantine%s' % (name, extension)
        self.assertTrue(os.path.exists(backup_name))
        backup_name = u'%s_quarantine_1%s' % (name, extension)
        self.assertTrue(os.path.exists(backup_name))
        backup_name = u'%s_quarantine_2%s' % (name, extension)
        self.assertTrue(os.path.exists(backup_name))

    def test_replace_missing(self):
        importer = SongImporter()
        filepath = './apps/yabase/fixtures/mp3/known_by_echonest_lastfm.mp3'

        metadata = uploader.get_file_infos(filepath)

        sm, _message = importer.import_song(filepath, metadata=metadata, convert=False, allow_unknown_song=True)
        self.assertIsNotNone(sm.yasound_song_id)

        yasound_song = YasoundSong.objects.get(id=sm.yasound_song_id)
        self.assertTrue(yasound_song.file_exists())
        path = yasound_song.get_song_path()
        os.remove(path)
        self.assertFalse(yasound_song.file_exists())

        sm, _message = importer.import_song(filepath, metadata=metadata, convert=False, allow_unknown_song=True)
        self.assertIsNotNone(sm.yasound_song_id)
        self.assertTrue(yasound_song.file_exists())
        new_path = yasound_song.get_song_path()
        self.assertEquals(path, new_path)

    def test_queen(self):
        importer = SongImporter()
        filepath = './apps/yabase/fixtures/mp3/queen_bontampi.mp3'

        metadata = {
            'title': 'innuendo',
            'artist': 'queen',
            'album': 'my album',
        }
        sm, _message = importer.import_song(filepath, metadata=metadata, convert=False, allow_unknown_song=True)
        self.assertIsNotNone(sm.yasound_song_id)

        yasound_song = YasoundSong.objects.get(id=sm.yasound_song_id)
        rank = yasound_song.find_lastfm_rank()
        self.assertTrue(rank < 0.8)

        filepath = './apps/yabase/fixtures/mp3/queen_verygood.m4a'
        metadata = uploader.get_file_infos(filepath)
        new_sm, _message = importer.import_song(filepath, metadata=metadata, convert=True, allow_unknown_song=True)
        self.assertIsNotNone(new_sm.yasound_song_id)

        new_yasound_song = YasoundSong.objects.get(id=new_sm.yasound_song_id)
        rank = new_yasound_song.find_lastfm_rank()
        self.assertTrue(rank > 0.9)
        self.assertNotEquals(new_yasound_song.id, yasound_song.id)

    def test_duplicate(self):
        importer = SongImporter()

        filepath = './apps/yabase/fixtures/mp3/known_by_echonest_lastfm.mp3'
        metadata = uploader.get_file_infos(filepath)
        sm, _message = importer.import_song(filepath, metadata=metadata, convert=False, allow_unknown_song=True)
        self.assertIsNotNone(sm.yasound_song_id)

        new_sm, _message = importer.import_song(filepath, metadata=metadata, convert=False, allow_unknown_song=True)
        self.assertEquals(new_sm.id, 2)


class TestRadioDeleted(TestCase):
    def setUp(self):
        erase_index()
        user = User(email="test@yasound.com", username="test", is_superuser=False, is_staff=False)
        user.set_password('test')
        user.save()
        Radio.objects.create(creator=user, ready=True)
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

        radio = Radio(name='uneradio', creator=self.user, ready=True)
        radio.save()

        results = Radio.objects.search_fuzzy('uneradio')
        self.assertEquals(len(results), 1)

        results = Radio.objects.search_fuzzy('test')
        self.assertEquals(len(results), 1)

        Radio.objects.radio_for_user(self.user).delete()

        results = Radio.objects.search_fuzzy('test')
        self.assertEquals(len(results), 0)

    def test_duplicates(self):
        radio = Radio(name='uneradio', ready=True, creator=self.user)
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

class TestSongInstanceDeleted(TestCase):
    def setUp(self):
        erase_index()
        user = User(email="test@yasound.com", username="test", is_superuser=False, is_staff=False)
        user.set_password('test')
        user.save()
        Radio.objects.create(creator=user)
        self.client.login(username="test", password="test")
        self.user = user

    def test_current_song(self):
        radio = Radio.objects.radio_for_user(self.user)

        playlist = generate_playlist(song_count=100)
        playlist.radio = radio
        playlist.save()

        si = SongInstance.objects.get(id=1)

        radio.current_song = si
        radio.save()

        si.delete()

        radio = Radio.objects.get(id=radio.id)
        self.assertEquals(radio.current_song_id, None)


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

    def testMostActiveRadios(self):
        Radio(name='test_radio', ready=True, creator=self.user).save()
        radios = Radio.objects.filter(ready=True)
        if radios.count() == 0:
            return
        radio_id = radios[0].id

        from yametrics.models import RadioPopularityManager
        import yametrics.settings as yametrics_settings
        m = RadioPopularityManager()
        m.drop()
        m.action(radio_id, yametrics_settings.ACTIVITY_ADD_TO_FAVORITES)

        url = '/api/v1/most_active_radio/'
        res = self.client.get(url)
        self.assertEquals(res.status_code, 200)

        data = res.content
        decoded_data = json.loads(data)
        meta = decoded_data['meta']
        self.assertGreater(meta['total_count'], 0)

        m.drop()

class TestWallPost(TestCase):
    def setUp(self):
        erase_index()
        user = User(email="test@yasound.com", username="test", is_superuser=True, is_staff=True)
        user.set_password('test')
        user.save()
        Radio.objects.create(creator=user)
        self.client.login(username="test", password="test")
        self.user = user
        self.key = ApiKey.objects.get(user=self.user).key
        self.username = self.user.username


        radio = Radio.objects.radio_for_user(self.user)
        playlist = generate_playlist(song_count=100)
        playlist.radio = radio
        playlist.save()

        self.radio = radio
        self.radio.current_song = SongInstance.objects.filter(playlist=playlist).order_by('?')[0]
        self.radio.save()

    def test_like_song(self):
        redis = Mock(name='redis')
        redis.publish = Mock()
        with patch('yabase.push.Redis') as mock_redis:
            mock_redis.return_value = redis
            song = SongInstance.objects.get(id=1)

            self.client.post(reverse('yabase.views.like_song', args=[song.id]))
            self.assertEquals(WallEvent.objects.filter(type=yabase_settings.EVENT_LIKE).count(), 1)

            self.client.post(reverse('yabase.views.like_song', args=[song.id]))
            self.assertEquals(WallEvent.objects.filter(type=yabase_settings.EVENT_LIKE).count(), 1)

            song = SongInstance.objects.get(id=2)

            self.client.post(reverse('yabase.views.like_song', args=[song.id]))
            self.assertEquals(WallEvent.objects.filter(type=yabase_settings.EVENT_LIKE).count(), 2)

            self.client.post(reverse('yabase.views.like_song', args=[song.id]))
            self.assertEquals(WallEvent.objects.filter(type=yabase_settings.EVENT_LIKE).count(), 2)

            song = SongInstance.objects.get(id=1)

            self.client.post(reverse('yabase.views.like_song', args=[song.id]))
            self.assertEquals(WallEvent.objects.filter(type=yabase_settings.EVENT_LIKE).count(), 3)

            self.client.post(reverse('yabase.views.like_song', args=[song.id]))
            self.assertEquals(WallEvent.objects.filter(type=yabase_settings.EVENT_LIKE).count(), 3)

            likes = WallEvent.objects.likes_for_user(self.user)
            self.assertEquals(likes.count(), 3)


    def test_post_message(self):
        redis = Mock(name='redis')
        redis.publish = Mock()
        with patch('yabase.push.Redis') as mock_redis:
            mock_redis.return_value = redis

            # post message
            res = self.client.post(reverse('yabase.views.post_message', args=[self.radio.uuid]), {'message': 'hello, world'})
            self.assertEquals(res.status_code, 200)
            self.assertEquals(WallEvent.objects.filter(type=yabase_settings.EVENT_MESSAGE).count(), 1)
            self.assertEquals(WallEvent.objects.filter(type=yabase_settings.EVENT_SONG).count(), 1)

            # delete posted message
            message = WallEvent.objects.filter(type=yabase_settings.EVENT_MESSAGE)[0]

            res = self.client.delete(reverse('yabase.views.delete_message', args=[message.id]))
            self.assertEquals(res.status_code, 200)
            self.assertEquals(WallEvent.objects.filter(type=yabase_settings.EVENT_MESSAGE).count(), 0)
            self.assertEquals(WallEvent.objects.filter(type=yabase_settings.EVENT_SONG).count(), 1)


            # post to another radio
            other_radio = Radio.objects.create(name='other')
            res = self.client.post(reverse('yabase.views.post_message', args=[other_radio.uuid]), {'message': 'hello, world'})
            self.assertEquals(res.status_code, 200)
            self.assertEquals(WallEvent.objects.filter(type=yabase_settings.EVENT_MESSAGE).count(), 1)
            self.assertEquals(WallEvent.objects.filter(type=yabase_settings.EVENT_SONG).count(), 1)

            # delete posted message : impossible because user is not the owner of radio
            message = WallEvent.objects.filter(type=yabase_settings.EVENT_MESSAGE, radio=other_radio)[0]

            res = self.client.delete(reverse('yabase.views.delete_message', args=[message.id]))
            self.assertEquals(res.status_code, 401)

    def test_report_message(self):
        redis = Mock(name='redis')
        redis.publish = Mock()
        with patch('yabase.push.Redis') as mock_redis:
            mock_redis.return_value = redis

            # post message
            res = self.client.post(reverse('yabase.views.post_message', args=[self.radio.uuid]), {'message': 'hello, world'})
            self.assertEquals(res.status_code, 200)
            self.assertEquals(WallEvent.objects.filter(type=yabase_settings.EVENT_MESSAGE).count(), 1)
            self.assertEquals(WallEvent.objects.filter(type=yabase_settings.EVENT_SONG).count(), 1)

            message = WallEvent.objects.filter(type=yabase_settings.EVENT_MESSAGE)[0]
            res = self.client.post(reverse('yabase.views.report_message_as_abuse', args=[message.id]))
            self.assertEquals(res.status_code, 200)

class TestDuplicate(TestCase):
    def setUp(self):
        erase_index()
        user = User(email="test@yasound.com", username="test", is_superuser=True, is_staff=True)
        user.set_password('test')
        user.save()
        Radio.objects.create(creator=user)
        self.client.login(username="test", password="test")
        self.user = user
        self.key = ApiKey.objects.get(user=self.user).key
        self.username = self.user.username


        radio = Radio.objects.radio_for_user(self.user)
        playlist = generate_playlist(song_count=100)
        playlist.radio = radio
        playlist.save()

        self.radio = radio

    def test_duplicate(self):
        song_count = SongInstance.objects.all().count()
        song_metadata = SongMetadata.objects.all().count()
        self.assertEquals(song_count, 100)
        self.assertEquals(song_metadata, 100)

        new_radio = self.radio.duplicate()
        self.assertEquals(new_radio.name, u'%s - copy' % self.radio.name)

        song_count = SongInstance.objects.all().count()
        song_metadata = SongMetadata.objects.all().count()
        self.assertEquals(song_count, 200)
        self.assertEquals(song_metadata, 100)

class TestBroadcastMessage(TestCase):
    def setUp(self):
        user = User(email="test@yasound.com", username="broadcast", is_superuser=True, is_staff=True)
        user.set_password('test')
        user.save()
        self.client.login(username="broadcast", password="test")
        self.user = user
        Radio.objects.create(creator=user)

    def test_broadcast_not_owner(self):
        other_radio = Radio.objects.create(name='other')
        res = self.client.post(reverse('yabase.views.radio_broadcast_message', args=[other_radio.uuid]), {'message': 'hello, world'})
        self.assertEquals(res.status_code, 403)

    def test_broadcast_ok(self):
        radio = Radio.objects.radio_for_user(self.user)
        res = self.client.post(reverse('yabase.views.radio_broadcast_message', args=[radio.uuid]), {'message': '<b>hello, world</b>'})
        self.assertEquals(res.status_code, 200)

class TestTags(TestCase):
    def setUp(self):
        user = User(email="test@yasound.com", username="test", is_superuser=True, is_staff=True)
        user.set_password('test')
        user.save()
        Radio.objects.create(creator=user)
        self.client.login(username="test", password="test")
        self.user = user

    def test_clean_tags(self):
        tags = clean_tags(['', ' ', 'hi, there', '   tag   ', " طبيب ", " Rock "])
        self.assertEquals(tags, ['hi, there', 'tag', "طبيب", 'rock'])

    def test_clean_radio(self):
        radio = Radio.objects.radio_for_user(self.user)
        input_tags = [u'', u' ', u'hi, there', u'   tag   ', u" طبيب ", u" Rock ", u'ok']

        radio.tags.add(*input_tags)
        tags = radio.tags.all()
        for tag in tags:
            self.assertTrue(tag.name in input_tags)

        Radio.objects.clean_tags()
        cleaned_input_tags = [u'hi, there', u'tag', u"طبيب", u'rock', u'ok']

        tags = radio.tags.all()
        self.assertEquals(tags.count(), len(cleaned_input_tags))
        for tag in tags:
            self.assertTrue(tag.name in cleaned_input_tags)

class TestParseItunes(TestCase):
    def test_parse_line(self):
        line = u'Vivement dimanche \t \t3:56\tDominique A\tLa Fossette\tChanson française      '
        name, album, artist = parse_itunes_line(line)
        self.assertEquals(name, u'Vivement dimanche')
        self.assertEquals(artist, 'Dominique A')
        self.assertEquals(album, 'La Fossette')


class TestSongInstanceOrder(TestCase):
    def setUp(self):
        self.user = User(email="test@yasound.com", username="test", is_superuser=False, is_staff=False)
        self.user.set_password('test')
        self.user.save()

        self.radio = Radio(creator=self.user)
        self.radio.save()
        self.playlist = Playlist.objects.create(radio=self.radio, name='main', source='src')

        nb_songs = 10
        for i in range(nb_songs):
            name = 'song-%d' % i
            artist = 'artist-%d' % i
            album = 'album-%d' % i
            y = YasoundSong(name=name, artist_name=artist, album_name=album, filename='nofile', filesize=0, duration=60)
            y.save()
            song_instance, _created = SongInstance.objects.create_from_yasound_song(self.playlist, y)
            song_instance.order = i
            song_instance.save()

    def test_setup(self):
        print '\n***** test_setup *****'
        songs = SongInstance.objects.filter(playlist=self.playlist).order_by('order')
        order = 0
        for s in songs:
            print s.order, s.metadata.name
            self.assertEqual(s.order, order)
            order += 1

    def test_insert(self):
        print '\n***** test_insert *****'
        insert_order = 3
        y = YasoundSong(name='test song', artist_name='test artist', album_name='test album', filename='nofile', filesize=0, duration=60)
        y.save()
        song_instance, _created = SongInstance.objects.create_from_yasound_song(self.playlist, y)
        song_instance.order = insert_order
        song_instance.save()

        songs = SongInstance.objects.filter(playlist=self.playlist).order_by('order')
        order = 0
        for s in songs:
            print s.order, s.metadata.name
            self.assertEqual(s.order, order)
            order += 1

    def test_reset_order(self):
        print '\n***** test_reset_order *****'
        order_to_reset = 2
        print 'reset order for song with order=%d' % order_to_reset
        s = SongInstance.objects.filter(playlist=self.playlist).order_by('order')[order_to_reset]
        s.order = None
        s.save()

        songs = SongInstance.objects.filter(playlist=self.playlist, order__isnull=False).order_by('order')
        order = 0
        for s in songs:
            print s.order, s.metadata.name
            self.assertEqual(s.order, order)
            order += 1

    def test_delete(self):
        print '\n***** test_delete *****'
        order_to_delete = 2
        print 'delete song with order=%d' % order_to_delete
        s = SongInstance.objects.filter(playlist=self.playlist).order_by('order')[order_to_delete]
        s.delete()

        songs = SongInstance.objects.filter(playlist=self.playlist, order__isnull=False).order_by('order')
        order = 0
        for s in songs:
            print s.order, s.metadata.name
            self.assertEqual(s.order, order)
            order += 1

    def test_move_up(self):
        print '\n***** test_move_up *****'
        old_order = 2
        new_order = 6
        print 'move song with order=%d to order=%d' % (old_order, new_order)
        s = SongInstance.objects.get(playlist=self.playlist, order=old_order)
        s.order = new_order
        s.save()

        songs = SongInstance.objects.filter(playlist=self.playlist, order__isnull=False).order_by('order')
        order = 0
        for s in songs:
            print s.order, s.metadata.name
            self.assertEqual(s.order, order)
            order += 1

    def test_move_down(self):
        print '\n***** test_move_down *****'
        old_order = 6
        new_order = 2
        print 'move song with order=%d to order=%d' % (old_order, new_order)
        s = SongInstance.objects.get(playlist=self.playlist, order=old_order)
        s.order = new_order
        s.save()

        songs = SongInstance.objects.filter(playlist=self.playlist, order__isnull=False).order_by('order')
        order = 0
        for s in songs:
            print s.order, s.metadata.name
            self.assertEqual(s.order, order)
            order += 1

    def test_multi(self):
        print '\n***** test_multi *****'

        s = SongInstance.objects.get(playlist=self.playlist, order=2)
        s.order = 5
        s.save()

        s = SongInstance.objects.get(playlist=self.playlist, order=3)
        s.order = 4
        s.save()

        s = SongInstance.objects.get(playlist=self.playlist, order=9)
        s.order = None
        s.save()

        s = SongInstance.objects.get(playlist=self.playlist, order=7)
        s.order = 4
        s.save()

        s = SongInstance.objects.get(playlist=self.playlist, order=6)
        s.order = 2
        s.save()

        s = SongInstance.objects.get(playlist=self.playlist, order=1)
        s.order = 4
        s.save()

        y = YasoundSong(name='test song', artist_name='test artist', album_name='test album', filename='nofile', filesize=0, duration=60)
        y.save()
        song_instance, _created = SongInstance.objects.create_from_yasound_song(self.playlist, y)
        song_instance.order = 3
        song_instance.save()

        s = SongInstance.objects.get(playlist=self.playlist, order=6)
        s.order = 0
        s.save()

        s = SongInstance.objects.get(playlist=self.playlist, order=2)
        s.order = None
        s.save()

        s = SongInstance.objects.get(playlist=self.playlist, order=4)
        s.delete()

        y = YasoundSong(name='test song 2', artist_name='test artist', album_name='test album', filename='nofile', filesize=0, duration=60)
        y.save()
        song_instance, _created = SongInstance.objects.create_from_yasound_song(self.playlist, y)
        song_instance.order = 8
        song_instance.save()

        s = SongInstance.objects.get(playlist=self.playlist, order=2)
        s.order = 7
        s.save()

        s = SongInstance.objects.get(playlist=self.playlist, order=2)
        s.order = 20 # too high, will be clipped
        s.save()

        y = YasoundSong(name='test song 4', artist_name='test artist', album_name='test album', filename='nofile', filesize=0, duration=60)
        y.save()
        song_instance, _created = SongInstance.objects.create_from_yasound_song(self.playlist, y)
        song_instance.order = 30 # too high
        song_instance.save()

        s = SongInstance.objects.get(playlist=self.playlist, order=1)
        s.order = 9
        s.save()

        songs = SongInstance.objects.filter(playlist=self.playlist, order__isnull=False).order_by('order')
        order = 0
        for s in songs:
            print s.order, s.metadata.name
            self.assertEqual(s.order, order)
            order += 1

    def test_edit_order_view(self):
        old_order = 3
        new_order = 5
        song = SongInstance.objects.get(playlist=self.playlist, order=old_order)
        s = {
             'id': song.id,
             'order': new_order
             }
        json_s = json.dumps(s)
        response = self.client.put('/api/v1/edit_song/%d/?username=%s&api_key=%s' % (song.id, self.user.username, self.user.api_key.key), json_s, content_type='application/json')
        self.assertEqual(response.status_code, 204)

        song = SongInstance.objects.get(id=song.id)
        self.assertEqual(song.order, new_order)

class TestProgramming(TestCase):
    def setUp(self):
        self.user = User(email="test@yasound.com", username="test", is_superuser=False, is_staff=False)
        self.user.set_password('test')
        self.user.save()
        Radio.objects.create(creator=self.user)
        self.client.login(username="test", password="test")

        self.radio = Radio.objects.radio_for_user(self.user)
        self.playlist, _created = self.radio.get_or_create_default_playlist()

        nb_songs = 10
        for i in range(nb_songs):
            name = 'song-%d' % i
            artist = 'artist-%d' % i
            album = 'album-%d' % i
            y = YasoundSong(name=name, artist_name=artist, album_name=album, filename='nofile', filesize=0, duration=60)
            y.save()
            song_instance, _created = SongInstance.objects.create_from_yasound_song(self.playlist, y)
            song_instance.order = i
            song_instance.save()


    def test_my_programming(self):
        url = reverse('yabase.views.my_programming', args=[self.radio.uuid])
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

        data = json.loads(response.content)
        self.assertEquals(data.get('meta').get('total_count'), 10)

    def test_my_programming_other_radio(self):
        radio = Radio(creator=self.user)
        radio.save()
        playlist = Playlist.objects.create(radio=radio, name='main', source='src')

        nb_songs = 5
        for i in range(nb_songs):
            name = 'song-%d' % i
            artist = 'artist-%d' % i
            album = 'album-%d' % i
            y = YasoundSong(name=name, artist_name=artist, album_name=album, filename='nofile', filesize=0, duration=60)
            y.save()
            song_instance, _created = SongInstance.objects.create_from_yasound_song(playlist, y)
            song_instance.order = i
            song_instance.save()

        response = self.client.get('/api/v1/radio/%s/programming/' % (radio.uuid))
        self.assertEquals(response.status_code, 200)

        data = json.loads(response.content)
        self.assertEquals(data.get('meta').get('total_count'), 5)

        response = self.client.get('/api/v1/radio/%s/programming/' % (self.radio.uuid))
        self.assertEquals(response.status_code, 200)

        data = json.loads(response.content)
        self.assertEquals(data.get('meta').get('total_count'), 10)


    def test_my_programming_remove_artist(self):
        radio = Radio(creator=self.user)
        radio.save()
        playlist = Playlist.objects.create(radio=radio, name='main', source='src')

        nb_songs = 5
        for i in range(nb_songs):
            name = 'song-%d' % i
            artist = 'artist-%d' % i
            album = 'album-%d' % i
            y = YasoundSong(name=name, artist_name=artist, album_name=album, filename='nofile', filesize=0, duration=60)
            y.save()
            song_instance, _created = SongInstance.objects.create_from_yasound_song(playlist, y)
            song_instance.order = i
            song_instance.save()

        response = self.client.get(reverse('yabase.views.my_programming', args=[self.radio.uuid]))
        self.assertEquals(response.status_code, 200)

        data = json.loads(response.content)
        self.assertEquals(data.get('meta').get('total_count'), 10)

        url = reverse('yabase.views.my_programming_artists', args=[self.radio.uuid])
        data = {
            'action': 'delete',
            'name': 'artist-1'
        }
        response = self.client.post(url, json.dumps(data), content_type="application/json")
        self.assertEquals(response.status_code, 200)
        response = self.client.get(reverse('yabase.views.my_programming', args=[self.radio.uuid]))
        data = json.loads(response.content)
        self.assertEquals(data.get('meta').get('total_count'), 9)

        # remove song with empty artist
        SongMetadata.objects.filter(artist_name='artist-4').update(artist_name='')
        url = reverse('yabase.views.my_programming_artists', args=[self.radio.uuid])
        data = {
            'action': 'delete',
            'name': ''
        }
        response = self.client.post(url, json.dumps(data), content_type="application/json")
        self.assertEquals(response.status_code, 200)
        response = self.client.get(reverse('yabase.views.my_programming', args=[self.radio.uuid]))
        data = json.loads(response.content)
        self.assertEquals(data.get('meta').get('total_count'), 8)


    def test_my_programming_remove_album(self):
        radio = Radio(creator=self.user)
        radio.save()
        playlist = Playlist.objects.create(radio=radio, name='main', source='src')

        nb_songs = 5
        for i in range(nb_songs):
            name = 'song-%d' % i
            artist = 'artist-%d' % i
            album = 'album-%d' % i
            y = YasoundSong(name=name, artist_name=artist, album_name=album, filename='nofile', filesize=0, duration=60)
            y.save()
            song_instance, _created = SongInstance.objects.create_from_yasound_song(playlist, y)
            song_instance.order = i
            song_instance.save()

        response = self.client.get(reverse('yabase.views.my_programming', args=[self.radio.uuid]))
        self.assertEquals(response.status_code, 200)

        data = json.loads(response.content)
        self.assertEquals(data.get('meta').get('total_count'), 10)

        url = reverse('yabase.views.my_programming_albums', args=[self.radio.uuid])
        data = {
            'action': 'delete',
            'name': 'album-1'
        }
        response = self.client.post(url, json.dumps(data), content_type="application/json")
        self.assertEquals(response.status_code, 200)
        response = self.client.get(reverse('yabase.views.my_programming', args=[self.radio.uuid]))
        data = json.loads(response.content)
        self.assertEquals(data.get('meta').get('total_count'), 9)

        url = reverse('yabase.views.my_programming_albums', args=[self.radio.uuid])
        data = {
            'action': 'delete',
            'name': ''
        }
        response = self.client.post(url, json.dumps(data), content_type="application/json")
        self.assertEquals(response.status_code, 200)
        response = self.client.get(reverse('yabase.views.my_programming', args=[self.radio.uuid]))
        data = json.loads(response.content)
        self.assertEquals(data.get('meta').get('total_count'), 9)

        url = reverse('yabase.views.my_programming_albums', args=[self.radio.uuid])
        data = {
            'action': 'delete',
        }
        response = self.client.post(url, json.dumps(data), content_type="application/json")
        self.assertEquals(response.status_code, 200)
        response = self.client.get(reverse('yabase.views.my_programming', args=[self.radio.uuid]))
        data = json.loads(response.content)
        self.assertEquals(data.get('meta').get('total_count'), 9)

        # remove song with empty album
        SongMetadata.objects.filter(album_name='album-4').update(album_name='')
        url = reverse('yabase.views.my_programming_albums', args=[self.radio.uuid])
        data = {
            'action': 'delete',
            'name': ''
        }
        response = self.client.post(url, json.dumps(data), content_type="application/json")
        self.assertEquals(response.status_code, 200)
        response = self.client.get(reverse('yabase.views.my_programming', args=[self.radio.uuid]))
        data = json.loads(response.content)
        self.assertEquals(data.get('meta').get('total_count'), 8)

class TestMyRadios(TestCase):
    def setUp(self):
        self.user = User(email="test@yasound.com", username="test", is_superuser=True, is_staff=False)
        self.user.set_password('test')
        self.user.save()
        Radio.objects.create(creator=self.user)

        self.client.login(username="test", password="test")

    def test_get_my_radios(self):
        url = reverse('yabase.views.my_radios')
        res = self.client.get(url)
        self.assertEquals(res.status_code, 200)
        data = res.content
        decoded_data = json.loads(data)
        meta = decoded_data['meta']
        self.assertEquals(meta['total_count'], 1)

        objects = decoded_data['objects']
        radio_data = objects[0]
        user_radio = Radio.objects.radio_for_user(self.user)

        self.assertEquals(radio_data["id"], user_radio.id)

    def test_post_my_radios(self):
        url = reverse('yabase.views.my_radios')
        res = self.client.post(url)
        self.assertEquals(res.status_code, 200)
        data = res.content
        new_radio = json.loads(data)

        self.assertEquals(new_radio['id'], 2)
        self.assertEquals(new_radio['creator']['username'], self.user.username)

        res = self.client.get(url)
        self.assertEquals(res.status_code, 200)
        data = res.content
        decoded_data = json.loads(data)
        meta = decoded_data['meta']
        self.assertEquals(meta['total_count'], 2)

    def test_delete_my_radios(self):
        url = reverse('yabase.views.my_radios')
        res = self.client.post(url)
        self.assertEquals(res.status_code, 200)
        data = res.content
        new_radio = json.loads(data)

        self.assertEquals(new_radio['id'], 2)
        self.assertEquals(new_radio['creator']['username'], self.user.username)

        res = self.client.get(url)
        self.assertEquals(res.status_code, 200)
        data = res.content
        decoded_data = json.loads(data)
        meta = decoded_data['meta']
        self.assertEquals(meta['total_count'], 2)


        url = reverse('yabase.views.my_radios', args=[new_radio['uuid']])
        res = self.client.delete(url)
        self.assertEquals(res.status_code, 200)

        url = reverse('yabase.views.my_radios')
        res = self.client.get(url)
        self.assertEquals(res.status_code, 200)
        data = res.content
        decoded_data = json.loads(data)
        meta = decoded_data['meta']
        self.assertEquals(meta['total_count'], 1)
