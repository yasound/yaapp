from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client
from yabase.models import Radio, SongInstance, NextSong
from yabase.tests_utils import generate_playlist


        
class TestRadioDeleted(TestCase):
    def setUp(self):
        user = User(email="test@yasound.com", username="test", is_superuser=True, is_staff=True)
        user.set_password('test')
        user.save()
        self.client.login(username="test", password="test")
        self.user = user   
    
    def test_remove_song_instance(self):
        radio = Radio.objects.radio_for_user(self.user)
        
        playlist = generate_playlist()
        playlist.radio = radio
        playlist.save()
        
        for i in range(1, 10):
            ns = NextSong(radio=radio, song=SongInstance.objects.get(id=i), order=i)
            ns.save()
            
        radio.current_song = SongInstance.objects.get(id=10)

        c = Client()
        c.login(username='test', password='test')
        r = c.post(reverse('yabackoffice.views.radio_remove_songs', args=[1]))
        self.assertEquals(r.status_code, 200)
        

class TestMetrics(TestCase):
    def setUp(self):
        user = User(email="test@yasound.com", username="test", is_superuser=True, is_staff=True)
        user.set_password('test')
        user.save()
        
    def test_light_metrics(self):
        res = self.client.get(reverse('light_metrics'))
        self.assertContains(res, '"user_count": 1')
        
        user = User(email='toto@yasound.com', username='toto')
        user.save()
        
        res = self.client.get(reverse('light_metrics'))
        self.assertContains(res, '"user_count": 2')
        
        
        