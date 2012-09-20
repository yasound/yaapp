# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.test import TestCase
from models import ClassifiedRadiosManager
from yabase import tests_utils as yabase_test_utils
from yabase.models import Radio, SongMetadata
from yarecommendation.models import MapArtistManager, RadioRecommendationsCache

class TestMapArtist(TestCase):
    def setUp(self):
        ma = MapArtistManager()
        ma.drop()

        user = User(email="test@yasound.com", username="test", is_superuser=False, is_staff=False)
        user.set_password('test')
        user.save()
        self.client.login(username="test", password="test")
        self.user = user

    def testManager(self):
        ma = MapArtistManager()
        artist = 'john'
        code = ma.artist_code(artist)
        self.assertEquals(code, 0)

        code = ma.artist_code(artist)
        self.assertEquals(code, 0)

        artist = 'jean'
        code = ma.artist_code(artist)
        self.assertEquals(code, 1)

        artist = 'john'
        code = ma.artist_code(artist)
        self.assertEquals(code, 0)

        artist = 'jeannot'
        code = ma.artist_code(artist)
        self.assertEquals(code, 2)

class TestClassification(TestCase):
    def setUp(self):
        cm = ClassifiedRadiosManager()
        cm.drop()

        ma = MapArtistManager()
        ma.drop()

        user = User(email="test@yasound.com", username="test", is_superuser=False, is_staff=False)
        user.set_password('test')
        user.save()
        self.client.login(username="test", password="test")
        self.user = user


    def testManager(self):
        ma = MapArtistManager()

        radio = Radio.objects.radio_for_user(self.user)
        playlist = yabase_test_utils.generate_playlist(song_count=10)
        playlist.radio = radio
        playlist.save()
        radio.ready=True
        radio.save()

        cm = ClassifiedRadiosManager()
        cm.add_radio(radio)

        doc = cm.all()[0]
        classification = doc.get('classification')
        self.assertEquals(classification.get(str(ma.artist_code('artist1'))), 1)


        SongMetadata.objects.filter(artist_name='artist2').update(artist_name='artist1')
        cm.add_radio(radio)

        doc = cm.all()[0]
        classification = doc.get('classification')
        self.assertEquals(classification.get(str(ma.artist_code('artist1'))), 2)


class TestCluster(TestCase):
    def setUp(self):
        cm = ClassifiedRadiosManager()
        cm.drop()

        rc = RadiosClusterManager()
        rc.drop()

        ma = MapArtistManager()
        ma.drop()

        user = User(email="test@yasound.com", username="test", is_superuser=False, is_staff=False)
        user.set_password('test')
        user.save()
        self.client.login(username="test", password="test")
        self.user = user

    def _generate_radios(self, n=10):
        radios = []
        for i in range(0, n):
            user = User.objects.create(email="test@yasound.com", username="%d" % (i), is_superuser=False, is_staff=False)
            radio = Radio.objects.create(name='%d' % (i), creator=user)
            playlist = yabase_test_utils.generate_playlist(song_count=10)
            playlist.radio = radio
            playlist.save()
            radio.ready=True
            radio.save()
            radios.append(radio)
        return radios


class TestRecommenationsCache(TestCase):
    def setUp(self):
        m = RadioRecommendationsCache()
        m.drop()
        self.manager = m

        user = User(email="test@yasound.com", username="test", is_superuser=False, is_staff=False)
        user.set_password('test')
        user.save()
        self.user = user

    def test_recomendations_save(self):
        radio_ids = [1, 5, 13, 73, 789, 55, 760]
        token = self.manager.save_recommendations(radio_ids)
        self.assertEqual(self.manager.recommendations.count(), 1)

        save_radio_ids = self.manager.get_recommendations(token)
        self.assertEqual(len(radio_ids), len(save_radio_ids))
        for i in range(len(radio_ids)):
            self.assertEqual(radio_ids[i], save_radio_ids[i])

    def test_artists_save(self):
        artists = ['the beatles', 'led zeppelin', 'mickael jackson', 'annie cordy', 'carlos']
        self.manager.save_artists(artists, self.user)
        self.assertEqual(self.manager.artists.count(), 1)

        saved_artists = self.manager.get_artists(self.user)
        self.assertEqual(len(artists), len(saved_artists))
        for i in range(len(artists)):
            self.assertEqual(artists[i], saved_artists[i])

    def test_recommendations_clean(self):
        radio_ids = [1, 5, 13, 73, 789, 55, 760]
        self.manager.save_recommendations(radio_ids)
        self.assertEqual(self.manager.recommendations.count(), 1)

        from datetime import datetime, timedelta
        self.manager.clean_deprecated_recommendations(-1)  # lifetime = -1 to be sure the recommendation save date is older than the limit
        self.assertEqual(self.manager.recommendations.count(), 0)
