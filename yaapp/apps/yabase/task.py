import sys
from celery.task import task
from yabase.models import Radio, Playlist, SongMetadata, SongInstance, YasoundSong, YasoundArtist, YasoundAlbum
import re

@task
def test(a):
    print 'testing task'
#    f = open('/Users/meeloo/Desktop/prout.txt', 'w')
#    f.write(a)
#    f.close()
    print 'testing task done YAY!'
    
    
@task
def process_playlists(radio, lines):
    PLAYLIST_TAG = 'LST'
    ARTIST_TAG = 'ART'
    ALBUM_TAG = 'ALB'
    SONG_TAG = 'SNG'

    artist_name = None
    album_name = None
    playlist = None
    
    pattern = re.compile('[\W_]+')

    for line in lines:
        elements = line.split(';')
        for i in range(len(elements)):
            elements[i] = elements[i].strip('"')
        tag = elements[0]
        if tag == PLAYLIST_TAG:
            playlist_name = elements[1]
            source_name = 'test_playlist_file'
            playlist, created = Playlist.objects.get_or_create(name=playlist_name, source=source_name)
            
        elif tag == ALBUM_TAG:
            album_name = elements[1]
        elif tag == ARTIST_TAG:
            artist_name = elements[1]
        elif tag == SONG_TAG:
            order = int(elements[1])
            song_name = elements[2]                
            metadata, created = SongMetadata.objects.get_or_create(name=song_name, artist_name=artist_name, album_name=album_name)
            song_instance, created = SongInstance.objects.get_or_create(playlist=playlist, metadata=metadata, order=order)
            if created:
                song_name_simplified = pattern.sub('', song_name.printable)
                artist_name_simplified = pattern.sub('', artist_name.printable)
                album_name_simplified = pattern.sub('', album_name.printable)
                yasound_song = YasoundSong.objects.get(name_simplified=song_name_simplified, artist__name_simplified=artist_name_simplified, album__name_simplified=album_name_simplified)
                if yasound_song:
                    song_instance.song = yasound_song.id
                
            
            
            
            
            
            