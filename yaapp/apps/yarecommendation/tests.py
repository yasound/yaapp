# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.test import TestCase
from models import ClassifiedRadiosManager
from yabase import tests_utils as yabase_test_utils
from yabase.models import Radio, SongMetadata
from yarecommendation.models import MapArtistManager

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


