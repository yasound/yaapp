# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.test import TestCase
from models import ClassifiedRadiosManager
from yabase import tests_utils as yabase_test_utils
from yabase.models import Radio
from yaref import test_utils as yaref_test_utils
from yaref.models import YasoundGenre, YasoundSongGenre, YasoundSong

class TestClassification(TestCase):
    def setUp(self):
        cm = ClassifiedRadiosManager()
        cm.drop()
        
        YasoundSong.objects.all().delete()
        YasoundGenre.objects.all().delete()
        
        user = User(email="test@yasound.com", username="test", is_superuser=False, is_staff=False)
        user.set_password('test')
        user.save()
        self.client.login(username="test", password="test")
        self.user = user        


    def testManager(self):
        for i in range(0, 10):
            YasoundGenre.objects.create(name='genre_%d' % (i), name_canonical = 'genre_%d' % (i))
        
        for i in range(0, 10):
            song = yaref_test_utils.generate_yasound_song(name='name %d' % (i), album='album', artist='artist')
            YasoundSongGenre.objects.create(song=song, genre=YasoundGenre.objects.get(id=i+1))

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
        self.assertEquals(classification.get('genre 0'), 1)

        song = YasoundSong.objects.get(id=2)        
        YasoundSongGenre.objects.create(song=song, genre=YasoundGenre.objects.get(id=1))
        cm.add_radio(radio)
        
        doc = cm.all()[0]
        classification = doc.get('classification')
        self.assertEquals(classification.get('genre 0'), 2)
        