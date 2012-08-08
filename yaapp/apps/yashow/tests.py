"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from models import ShowManager
from datetime import datetime
from django.contrib.auth.models import User
from yabase.models import Radio
from yaref.models import YasoundSong
from django.test import Client
from tastypie.models import ApiKey
import json

class ShowTest(TestCase):
    def setUp(self):
        self.manager = ShowManager()
        self.manager.shows.drop()
        
    def test_creation(self):
        user = User(email="test@yasound.com", username="test", is_superuser=False, is_staff=False)
        user.set_password('test')
        user.save()
            
        radio = Radio(creator=user)
        radio.save()
        
        d = self.manager.MONDAY
        t = datetime.now().time()
        show = self.manager.create_show('my first show', radio, d, t)
        self.assertIsNotNone(show)
        
        shows = self.manager.shows_for_radio(radio.id)
        self.assertEquals(shows.count(), 1)
        
    def test_get_show(self):
        user = User(email="test@yasound.com", username="test", is_superuser=False, is_staff=False)
        user.set_password('test')
        user.save()
            
        radio = Radio(creator=user)
        radio.save()
        
        d = self.manager.MONDAY
        t = datetime.now().time()
        show = self.manager.create_show('my first show', radio, d, t)
        self.assertIsNotNone(show)
        
        # show_id as ObjectId
        show_id = show['_id']
        s = self.manager.get_show(show_id)
        self.assertEqual(s['playlist_id'], show['playlist_id'])
        self.assertEqual(s['day'], show['day'])
        self.assertEqual(s['time'], show['time'])
        
        # show_id as str
        show_id = str(show['_id'])
        s = self.manager.get_show(show_id)
        self.assertEqual(s['playlist_id'], show['playlist_id'])
        self.assertEqual(s['day'], show['day'])
        self.assertEqual(s['time'], show['time'])
        
        # show_id as unicode
        show_id = unicode(show['_id'])
        s = self.manager.get_show(show_id)
        self.assertEqual(s['playlist_id'], show['playlist_id'])
        self.assertEqual(s['day'], show['day'])
        self.assertEqual(s['time'], show['time'])
        
        # check it returns None when an invalid id is asked
        show_id = '5020ece0f43a812199000001' # random id
        s = self.manager.get_show(show_id)
        self.assertIsNone(s)
        
    def test_update_show(self):
        user = User(email="test@yasound.com", username="test", is_superuser=False, is_staff=False)
        user.set_password('test')
        user.save()
            
        radio = Radio(creator=user)
        radio.save()
        
        d = self.manager.MONDAY
        t = datetime.now().time()
        show = self.manager.create_show('my first show', radio, d, t)
        self.assertIsNotNone(show)
        
        # change 'day'
        new_day = self.manager.WEDNESDAY
        show['day'] = new_day
        s = self.manager.update_show(show)
        
        # check returned data
        self.assertEqual(s['day'], new_day)
        
        # check stored data
        s2 = self.manager.get_show(s['_id'])
        self.assertEqual(s2['day'], new_day)
        
    def test_delete_show(self):
        user = User(email="test@yasound.com", username="test", is_superuser=False, is_staff=False)
        user.set_password('test')
        user.save()
            
        radio = Radio(creator=user)
        radio.save()
        
        show1 = self.manager.create_show('my first show', radio, self.manager.MONDAY, datetime.now().time())
        self.assertIsNotNone(show1)
        
        show2 = self.manager.create_show('my second show', radio, self.manager.TUESDAY, datetime.now().time())
        self.assertIsNotNone(show2)
        
        self.assertEqual(self.manager.shows.find().count(), 2)
        self.manager.delete_show(show1['_id'])
        self.assertEqual(self.manager.shows.find().count(), 1)
        
    def test_get_songs(self):
        user = User(email="test@yasound.com", username="test", is_superuser=False, is_staff=False)
        user.set_password('test')
        user.save()
            
        radio = Radio(creator=user)
        radio.save()
        
        nb_songs = 10
        for i in range(nb_songs):
            name = 'song-%d' % i
            artist = 'artist-%d' % i
            album = 'album-%d' % i
            y = YasoundSong(name=name, artist_name=artist, album_name=album, filename='nofile', filesize=0, duration=60)
            y.save()
        
        yasound_songs = YasoundSong.objects.all()[:nb_songs]
        
        d = self.manager.MONDAY
        t = datetime.now().time()
        show = self.manager.create_show('my first show', radio, d, t, yasound_songs=yasound_songs)
        self.assertIsNotNone(show)
        
        show_id = show['_id']
        songs = self.manager.songs_for_show(show_id)
        self.assertIsNotNone(songs)
        self.assertEqual(songs.count(), len(yasound_songs))

    def test_add_song(self):
        user = User(email="test@yasound.com", username="test", is_superuser=False, is_staff=False)
        user.set_password('test')
        user.save()
            
        radio = Radio(creator=user)
        radio.save()
        
        show = self.manager.create_show('my first show', radio, self.manager.MONDAY, datetime.now().time())
        self.assertIsNotNone(show)
        show_id = show['_id']
        
        nb_songs = self.manager.songs_for_show(show_id).count()
        self.assertEqual(nb_songs, 0)
        
        y = YasoundSong(name='test song', artist_name='test artist', album_name='test album', filename='nofile', filesize=0, duration=60)
        y.save()
        ok = self.manager.add_song_in_show(show_id, y.id)
        self.assertEqual(ok, True)
        nb_songs = self.manager.songs_for_show(show_id).count()
        self.assertEqual(nb_songs, 1)
        
    def test_remove_song(self):
        user = User(email="test@yasound.com", username="test", is_superuser=False, is_staff=False)
        user.set_password('test')
        user.save()
            
        radio = Radio(creator=user)
        radio.save()
        
        show = self.manager.create_show('my first show', radio, self.manager.MONDAY, datetime.now().time())
        show_id = show['_id']
        
        y = YasoundSong(name='test song', artist_name='test artist', album_name='test album', filename='nofile', filesize=0, duration=60)
        y.save()
        self.manager.add_song_in_show(show_id, y.id)
        
        song_instances = self.manager.songs_for_show(show_id)
        s = song_instances[0]
        song_instance_id = s.id
        
        ok = self.manager.remove_song(song_instance_id)
        self.assertEqual(ok, True)
        
        nb_songs = self.manager.songs_for_show(show_id).count()
        self.assertEqual(nb_songs, 0)
        
        

class ViewsTest(TestCase):
    def setUp(self):
        self.manager = ShowManager()
        self.manager.shows.drop()
        
        self.user = User(email="test@yasound.com", username="test", is_superuser=False, is_staff=False)
        self.user.set_password('test')
        self.user.save()
            
        self.radio = Radio(creator=self.user)
        self.radio.save()
        
        self.api_key = ApiKey.objects.get(user=self.user)
        
    def test_get_show(self):
        show = self.manager.create_show('my first show', self.radio, self.manager.MONDAY, datetime.now().time())
        show_id = show['_id']
        
        c = Client()
        response = c.get('/api/v1/show/%s/' % show_id, {'username':self.user.username, 'api_key':self.api_key.key})
        self.assertEqual(response.status_code, 200)
        
        s = json.loads(response.content)
        self.assertEqual(show['playlist_id'], s['playlist_id'])
        self.assertEqual(show['day'], s['day'])
        self.assertEqual(show['time'], s['time'])
        
    def test_get_shows(self):
        show1 = self.manager.create_show('my first show', self.radio, self.manager.MONDAY, datetime.now().time())
        show2 = self.manager.create_show('my second show', self.radio, self.manager.WEDNESDAY, datetime.now().time())
        show3 = self.manager.create_show('my third show', self.radio, self.manager.FRIDAY, datetime.now().time())
        
        # normal
        c = Client()
        response = c.get('/api/v1/radio/%s/shows/' % self.radio.uuid, {'username':self.user.username, 'api_key':self.api_key.key})
        self.assertEqual(response.status_code, 200)
        
        resp = json.loads(response.content)
        shows = resp['objects']
        self.assertEqual(len(shows), 3)
        self.assertEqual(shows[0]['playlist_id'], show1['playlist_id'])
        self.assertEqual(shows[1]['playlist_id'], show2['playlist_id'])
        self.assertEqual(shows[2]['playlist_id'], show3['playlist_id'])
        
        # skip & limit
        response = c.get('/api/v1/radio/%s/shows/' % self.radio.uuid, {'username':self.user.username, 'api_key':self.api_key.key, 'offset':1, 'limit':1})
        self.assertEqual(response.status_code, 200)
        
        resp = json.loads(response.content)
        shows = resp['objects']
        self.assertEqual(len(shows), 1)
        self.assertEqual(shows[0]['playlist_id'], show2['playlist_id'])
        
    def test_delete_show(self):
        show1 = self.manager.create_show('my first show', self.radio, self.manager.MONDAY, datetime.now().time())
        show2 = self.manager.create_show('my second show', self.radio, self.manager.WEDNESDAY, datetime.now().time())
    
        c = Client()
        response = c.delete('/api/v1/show/%s/?username=%s&api_key=%s' % (show1['_id'], self.user.username, self.api_key.key))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.manager.nb_shows_for_radio(self.radio.id), 1)
        
    def test_put_show(self):
        show = self.manager.create_show('my first show', self.radio, self.manager.MONDAY, datetime.now().time())
        show_id = show['_id']
        
        c = Client()
        response = c.get('/api/v1/show/%s/' % show_id, {'username':self.user.username, 'api_key':self.api_key.key})
        s = json.loads(response.content)
        new_day = self.manager.SUNDAY
        s['day'] = new_day
        
        response = c.put('/api/v1/show/%s/?username=%s&api_key=%s' % (s['_id'], self.user.username, self.api_key.key), s)
        self.assertEqual(response.status_code, 200)
        s = json.loads(response.content)
        self.assertEqual(s['day'], new_day)
        