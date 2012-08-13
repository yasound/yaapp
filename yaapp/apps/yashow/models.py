from django.db import models
from django.conf import settings
from yabase.models import Radio, Playlist, SongInstance, SongMetadata
from yaref.models import YasoundSong
import datetime
from bson.objectid import ObjectId
from pymongo import ASCENDING

def time_string_from_date_string(date_str):
    tokens = date_str.split('T')
    if len(tokens) == 1:
        return date_str
    return tokens[1]

class ShowManager():
    MONDAY = 'MON'
    TUESDAY = 'TUE'
    WEDNESDAY = 'WED'
    THURSDAY = 'THU'
    FRIDAY = 'FRI'
    SATURDAY = 'SAT'
    SUNDAY = 'SUN'
    
    
    TYPE_PLAYLIST = 'playlist'
    TYPE_META = 'meta'
    
    META_NEW_SONGS = 'new_songs'
    META_TOP_SONGS = 'top_songs'
    META_RARE_SONGS = 'rare_songs'
    
    def __init__(self):
        self.db = settings.MONGO_DB
        self.shows = self.db.shows
        self.shows.ensure_index("playlist_id", unique=True)
        
    def create_show(self, name, radio, days, time, random_play=True, enabled=True, yasound_songs=[]):        
        playlist = Playlist.objects.create(radio=radio, name=name)
        
        for index, y_song in enumerate(yasound_songs):
            if isinstance(y_song, int): # array of ids instead of objects
                try:
                    y_song = YasoundSong.objects.get(id=y_song)
                except:
                    pass
            if not isinstance(y_song, YasoundSong):
                continue
            song_instance, _created = SongInstance.objects.create_from_yasound_song(playlist=playlist, yasound_song=y_song)
            song_instance.order = index
            song_instance.save()
        
        if type(time) == datetime.time:
            time = time.isoformat()
        elif isinstance(time, str) or isinstance(time, unicode):
            time = time_string_from_date_string(time)
        
        show_doc = {'name': name,
                    'playlist_id': playlist.id,
                    'days': days,
                    'time': time,
                    'random_play': random_play,
                    'enabled': enabled,
                    'type': self.TYPE_PLAYLIST
                    }
        self.shows.insert(show_doc, safe=True)
        return self.shows.find_one({'playlist_id': playlist.id})
    
    def shows_for_radio(self, radio_id, count=None, skip=0):
        playlist_ids = Playlist.objects.filter(radio__id=radio_id).values_list('id', flat=True)
        
        query = {
                 'playlist_id': {'$in': list(playlist_ids)}
                 }
        
        if count is not None:
            shows = self.shows.find(query).sort([('playlist_id', ASCENDING)]).skip(skip).limit(count)
        else:
            shows = self.shows.find(query).sort([('playlist_id', ASCENDING)]).skip(skip)
        return shows
    
    def nb_shows_for_radio(self, radio_id):
        playlist_ids = Playlist.objects.filter(radio__id=radio_id).values_list('id', flat=True)
        query = {
                 'playlist_id': {'$in': list(playlist_ids)}
                 }
        count = self.shows.find(query).count()
        return count
    
    def get_show(self, show_id):
        if isinstance(show_id, str) or isinstance(show_id, unicode):
            show_id = ObjectId(show_id)
        return self.shows.find_one({'_id': show_id})
    
    def update_show(self, show_data):
        show_id = show_data.get('_id', None)
        if show_id and (isinstance(show_id, str) or isinstance(show_id, unicode)):
            show_data['_id'] = ObjectId(show_id)
        time = show_data['time']
        if time and (isinstance(time, str) or isinstance(time, unicode)):
            show_data['time'] = time_string_from_date_string(time)
        self.shows.update({'_id':show_data['_id']}, show_data, safe=True)
        return self.get_show(show_id)
    
    def delete_show(self, show_id):
        if show_id and (isinstance(show_id, str) or isinstance(show_id, unicode)):
            show_id = ObjectId(show_id)
        show = self.get_show(show_id)
        if show is None:
            return
        playlist = Playlist.objects.get(id=show['playlist_id'])
        playlist.delete()
        self.shows.remove({'_id': show_id})
        
    def duplicate_show(self, show_id):
        show_original = self.get_show(show_id)
        if show_original is None:
            return None
        
        radio = Playlist.objects.get(id=show_original['playlist_id']).radio
        days = show_original['days']
        time = show_original['time']
        random = show_original['random_play']
        name = show_original['name']
        enabled = show_original['enabled']
        yasound_songs = []
        songs_original = self.songs_for_show(show_id)
        for s in songs_original:
            yasound_song_id = s.metadata.yasound_song_id
            y = YasoundSong.objects.get(id=yasound_song_id)
            yasound_songs.append(y)
        
        show_copy = self.create_show(name, radio, days, time, random, enabled, yasound_songs)
        return show_copy
    
    def songs_for_show(self, show_id, count=None, skip=0):
        s = self.get_show(show_id)
        playlist_id = s['playlist_id']
        songs = SongInstance.objects.filter(playlist__id=playlist_id).order_by('order', 'id')
        if count is not None:
            songs = songs[skip:skip+count]
        else:
            songs = songs[skip:]
        return songs
    
    def add_song_in_show(self, show_id, yasound_song_id):
        show = self.get_show(show_id)
        if show is None:
            return False
        try:
            p = Playlist.objects.get(id=show['playlist_id'])
            y = YasoundSong.objects.get(id=yasound_song_id)
        except:
            return False
        song_count = SongInstance.objects.filter(playlist=p).count()
        song_instance, _created = SongInstance.objects.create_from_yasound_song(playlist=p, yasound_song=y)
        song_instance.order = song_count
        song_instance.save()
        return True
    
    def remove_song(self, song_instance_id):
        try:
            SongInstance.objects.get(id=song_instance_id).delete()
        except:
            return False
        return True
            
        
