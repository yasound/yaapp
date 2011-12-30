import sys
from celery.task import task
from yabase.models import Radio, Playlist, SongMetadata, SongInstance, YasoundSong, YasoundArtist, YasoundAlbum
import re
from django.db import transaction

@transaction.commit_on_success
def process_playlists_exec(radio, lines):
    print '*** process_playlists ***'
    PLAYLIST_TAG = 'LST'
    ARTIST_TAG = 'ART'
    ALBUM_TAG = 'ALB'
    SONG_TAG = 'SNG'

    artist_name = None
    album_name = None
    playlist = None
    
    pattern = re.compile('[\W_]+')

    count = 0
    found = 0
    notfound = 0
    

    for line in lines:
        elements = line.split(';')
        for i in range(len(elements)):
            elements[i] = elements[i].strip('"')
        tag = elements[0]
        if tag == PLAYLIST_TAG:
            playlist_name = elements[1]
            source_name = 'test_playlist_file'
            playlist, created = Playlist.objects.get_or_create(name=playlist_name, source=source_name)
            if created:
                print 'playlist created '
                print playlist
            else:
                print 'playlist found '
                print playlist
            
        elif tag == ALBUM_TAG:
            album_name = elements[1]
        elif tag == ARTIST_TAG:
            artist_name = elements[1]
        elif tag == SONG_TAG:
            order = int(elements[1])
            song_name = elements[2]                
            metadata, created = SongMetadata.objects.get_or_create(name=song_name, artist_name=artist_name, album_name=album_name)
            try:
                song_instance = SongInstance.objects.get(playlist=playlist, metadata=metadata, order=order)
                created = 0
            except SongInstance.DoesNotExist:
                song_instance = SongInstance(playlist=playlist, metadata=metadata, order=order)
                created = 1
            if created or song_instance.song == 0:
                song_name_simplified = pattern.sub('', song_name).lower()
                artist_name_simplified = pattern.sub('', artist_name).lower()
                album_name_simplified = pattern.sub('', album_name).lower()
                count += 1
                try:
                    yasound_song = YasoundSong.objects.get(name_simplified=song_name_simplified, artist_name_simplified=artist_name_simplified, album_name_simplified=album_name_simplified)
#                    yasound_songs = YasoundSong.objects.filter(name=song_name, artist_name=artist_name, album_name=album_name)
                    song_instance.song = yasound_song.id
                    song_instance.save()
                    found += 1
                    
                except YasoundSong.DoesNotExist:
                    notfound += 1
                    pass

    print 'found: %d - not found: %d - total: %d' % (found, notfound, count)
                    
                
            
@task
def process_playlists(radio, lines):
    return process_playlists_exec(radio, lines)

            
            
            
            
            
