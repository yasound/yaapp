from django.db import models
from django.conf import settings
from yabase.models import Radio, Playlist, SongInstance, SongMetadata
from yaref.models import YasoundSong
import datetime
from bson.objectid import ObjectId
from pymongo import ASCENDING

class ShowManager():
    MONDAY = 'MON'
    TUESDAY = 'TUE'
    WEDNESDAY = 'WED'
    THURSDAY = 'THU'
    FRIDAY = 'FRI'
    SATURDAY = 'SAT'
    SUNDAY = 'SUN'
    EVERY_DAY = 'ALL'
    
    DAYS = [MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY, SUNDAY, EVERY_DAY]
    
    TYPE_PLAYLIST = 'playlist'
    TYPE_META = 'meta'
    
    META_NEW_SONGS = 'new_songs'
    META_TOP_SONGS = 'top_songs'
    META_RARE_SONGS = 'rare_songs'
    
    def __init__(self):
        self.db = settings.MONGO_DB
        self.shows = self.db.shows
        self.shows.ensure_index("playlist_id", unique=True)
        
    def create_show(self, name, radio, day, time, random_play=True, yasound_songs=[]):
        if not day in self.DAYS:
            return None
        
        playlist = Playlist.objects.create(radio=radio, name=name)
        
        for y_song in yasound_songs:
            _song_instance = SongInstance.objects.create_from_yasound_song(playlist=playlist, yasound_song=y_song)
        
        if type(time) == datetime.time:
            time = time.isoformat()
        
        show_doc = {'name': name,
                    'playlist_id': playlist.id,
                    'day': day,
                    'time': time,
                    'random_play': random_play,
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
        self.shows.update({'_id':show_data['_id']}, show_data, safe=True)
        return self.get_show(show_id)
    
    def delete_show(self, show_id):
        if show_id and (isinstance(show_id, str) or isinstance(show_id, unicode)):
            show_id = ObjectId(show_id)
        self.shows.remove({'_id': show_id})
    
    def songs_for_show(self, show_id):
        s = self.get_show(show_id)
        playlist_id = s['playlist_id']
        songs = SongInstance.objects.filter(playlist__id=playlist_id)
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
        _song_instance = SongInstance.objects.create_from_yasound_song(playlist=p, yasound_song=y)
        return True
    
    def remove_song(self, song_instance_id):
        try:
            SongInstance.objects.get(id=song_instance_id).delete()
        except:
            return False
        return True
            
        
                                                       
                                                       
                                                       
                                                       