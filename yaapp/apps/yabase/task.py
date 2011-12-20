import sys
from celery.task import task
from yabase.models import Radio, Playlist, SongMetadata, SongInstance


@task
def test(a):
    print 'testing task'
#    f = open('/Users/meeloo/Desktop/prout.txt', 'w')
#    f.write(a)
#    f.close()
    print 'testing task done YAY!'
    
    
@task
def process_playlists(radio, lines):
    print 'process_playlists'
    
    
    print 'nb lines: %d' % len(lines)

    ACTION_ADD_TAG = 'ADD'
    ACTION_DEL_TAG = 'DEL'
    PLAYLIST_TAG = 'LST'
    ARTIST_TAG = 'ART'
    ALBUM_TAG = 'ALB'
    SONG_TAG = 'SNG'

    action = None;
    artist_name = None
    album_name = None
    playlist = None

    for line in lines:
        elements = line.split(';')
        for i in range(len(elements)):
            elements[i] = elements[i].strip('"')
        tag = elements[0]
        if tag == ACTION_ADD_TAG:
            action = ACTION_ADD_TAG
        elif tag == ACTION_DEL_TAG:
            action = ACTION_DEL_TAG
        elif tag == PLAYLIST_TAG:
            playlist_name = elements[1]
            source_name = 'test_playlist_file'
            if action == ACTION_ADD_TAG:
                print 'ADD playlist'
                playlist, created = Playlist.objects.get_or_create(name=playlist_name, source=source_name)
                if created:
                    print 'playlist created: '
                else:
                    print 'playlist found: '
                print playlist
            elif action == ACTION_DEL_TAG:
                try:
                    playlist = Playlist.objects.get(name=playlist_name, source=source_name)
                    playlist.delete()
                    print 'playlist deleted: '
                    print playlist
                except Playlist.DoesNotExist:
                    pass
            
        elif tag == ALBUM_TAG:
            album_name = elements[1]
        elif tag == ARTIST_TAG:
            artist_name = elements[1]
        elif tag == SONG_TAG:
            order = int(elements[1])
            song_name = elements[2]
            if action == ACTION_ADD_TAG:
                metadata, created = SongMetadata.objects.get_or_create(name=song_name, artist_name=artist_name, album_name=album_name)
#                if created:
#                    print 'metadata created'
#                else:
#                    print 'metadata found'
#                    print metadata
#                    print metadata.id
                song_instance, created = SongInstance.objects.get_or_create(playlist=playlist, metadata=metadata, order=order)
#                if created:
#                    print 'song created'
#                else:
#                    print 'song found'
            elif action == ACTION_DEL_TAG:
                try: 
                    metadata = SongMetadata.objects.get(name=song_name, artist_name=artist_name, album_name=album_name)
                    metadata.delete()
                    song_instance = SongInstance.objects.get(playlist=playlist, metadata=metadata, order=order)
                    song_instance.delete()
                except (SongMetadata.DoesNotExist, SongInstance.DoesNotExist):
                    pass 
                
            
            
            
            
            
            