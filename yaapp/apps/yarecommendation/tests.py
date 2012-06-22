# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.test import TestCase
from models import ClassifiedRadiosManager
from yabase import tests_utils as yabase_test_utils
from yabase.models import Radio, SongMetadata
from yaref import test_utils as yaref_test_utils
from yaref.models import YasoundGenre, YasoundSongGenre, YasoundSong

class TestClassification(TestCase):
    def setUp(self):
        cm = ClassifiedRadiosManager()
        cm.drop()
        
        user = User(email="test@yasound.com", username="test", is_superuser=False, is_staff=False)
        user.set_password('test')
        user.save()
        self.client.login(username="test", password="test")
        self.user = user        


    def testManager(self):
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
        self.assertEquals(classification.get('artist1'), 1)

        
        SongMetadata.objects.filter(artist_name='artist2').update(artist_name='artist1')
        cm.add_radio(radio)
        
        doc = cm.all()[0]
        classification = doc.get('classification')
        self.assertEquals(classification.get('artist1'), 2)
