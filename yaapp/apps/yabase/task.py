from celery.task import task
from django.db import transaction
from struct import *
from yabase.models import Radio, Playlist, SongMetadata, SongInstance, update_leaderboard
from yaref.models import YasoundSong
import re
import sys
import time
import zlib
from yaref.utils import get_simplified_name
import string
import settings as yabase_settings

@task
def leaderboard_update_task():
    update_leaderboard()
    

class BinaryData:
    def __init__(self, data):
        self.offset = 0
        self.data = data

    def get_int16(self):
        res = unpack_from('<h', self.data, self.offset)[0]
        self.offset = self.offset + 2
        return res

    def get_int32(self):
        res = unpack_from('<i', self.data, self.offset)[0]
        self.offset = self.offset + 4
        return res

    def get_tag(self):
        res = unpack_from('<4s', self.data, self.offset)[0]
        self.offset = self.offset + 4
        return res

    def get_string(self):
        size = self.get_int16()
        res = unpack_from('<' + str(size) + 's', self.data, self.offset)[0]
        self.offset = self.offset + size
        return res

    def is_done(self):
        return self.offset >= len(self.data)


@transaction.commit_on_success
def process_playlists_exec(radio, content_compressed):
    print "decompress playlist"
    content_uncompressed = zlib.decompress(content_compressed)

    print '*** process_playlists ***'
    PLAYLIST_TAG = 'LIST'
    ARTIST_TAG = 'ARTS'
    ALBUM_TAG = 'ALBM'
    SONG_TAG = 'SONG'
    UUID_TAG = 'UUID'
    REMOVE_PLAYLIST = 'REMV'
    REMOTE_PLAYLIST = 'RLST'
    
    artist_name = None
    album_name = None
    playlist = None
    uuid = 'unknown'

    pattern = re.compile('[\W_]+')

    count = 0
    found = 0
    notfound = 0


    data = BinaryData(content_uncompressed)

    while not data.is_done():
        tag = data.get_tag()
        if tag == UUID_TAG:
            uuid = data.get_string()
        
        elif tag == PLAYLIST_TAG:
            playlist_name = data.get_string()
            playlist, created = Playlist.objects.get_or_create(name=playlist_name, source=uuid, radio=radio)
            playlist.enabled = True
            playlist.save()
        elif tag == ALBUM_TAG:
            album_name = data.get_string()
            album_name_simplified = get_simplified_name(album_name)
        elif tag == ARTIST_TAG:
            artist_name = data.get_string()
            artist_name_simplified = get_simplified_name(artist_name)
        elif tag == SONG_TAG:
            order = data.get_int32()
            song_name = data.get_string()
            song_name_simplified = get_simplified_name(song_name)

            raw = SongMetadata.objects.raw("SELECT * from yabase_songmetadata WHERE name=%s and artist_name=%s and album_name=%s",
                                           [song_name,
                                            artist_name,
                                            album_name])
            if raw and len(list(raw)) > 0:
                metadata = list(raw)[0]
            else:
                metadata = SongMetadata(name=song_name, artist_name=artist_name, album_name=album_name)
                metadata.save()

            raw = SongInstance.objects.raw('SELECT * FROM yabase_songinstance WHERE playlist_id=%s and metadata_id=%s and "order"=%s',
                                           [playlist.id,
                                            metadata.id,
                                            order])
            if raw and len(list(raw)) > 0:
                song_instance = list(raw)[0]
            else:
                song_instance = SongInstance(playlist=playlist, metadata=metadata, order=order, frequency=0.5, enabled=True)

            if metadata.yasound_song_id == None:
                song_name_simplified = get_simplified_name(song_name)
                count += 1
                # let's go fuzzy
                mongo_doc = YasoundSong.objects.find_fuzzy(song_name_simplified.decode('utf-8', 'ignore'), 
                                                           album_name_simplified.decode('utf-8', 'ignore'), 
                                                           artist_name_simplified.decode('utf-8', 'ignore'))
                if not mongo_doc:
                    notfound += 1
                else:
                    metadata.yasound_song_id = mongo_doc['db_id']
                    metadata.save()
                    
                    song_instance.need_sync = False
                    found +=1
                    
                song_instance.save()
        elif tag == REMOVE_PLAYLIST:
            playlist_name = data.get_string()
            source = data.get_string()
            Playlist.objects.filter(name=playlist_name, source=source).update(enabled=False)
        elif tag == REMOTE_PLAYLIST:
            playlist_name = data.get_string()
            source = data.get_string()
            Playlist.objects.filter(name=playlist_name, source=source).update(enabled=True)
            
    songs_ok = SongInstance.objects.filter(playlist__in=radio.playlists.all(), song__gt=0)
    if songs_ok.count() > 0:
        radio.ready = True
        radio.save()
        radio.fill_next_songs_queue()
        
    print 'found: %d - not found: %d - total: %d' % (found, notfound, count)



@task
def process_playlists(radio, content_compressed):
    return process_playlists_exec(radio, content_compressed)


def process_need_sync_songs_exec():
    """
    try to match all needed sync songs with the yasound songs
    """
    songs = SongInstance.objects.filter(need_sync=True, metadata__yasound_song_id__isnull=True).select_related()
    for song in songs:
        metadata = song.metadata
        if not metadata:
            continue
        name = metadata.name
        album = metadata.album_name
        artist = metadata.artist_name
        mongo_doc = YasoundSong.objects.find_fuzzy(name, album, artist) 
        if mongo_doc:
            metadata.yasound_song_id = mongo_doc['db_id']
            metadata.save()
            song.need_sync = False
            song.save()
    
@task
def process_need_sync_songs():
    return process_need_sync_songs_exec()


