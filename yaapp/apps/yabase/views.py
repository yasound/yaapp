from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from yabase.models import Radio, Playlist, SongMetadata, SongInstance
import zlib

@csrf_exempt
def upload_playlists(request, radio_id):
    radio = get_object_or_404(Radio, pk=radio_id)

    print 'upload_playlists'
    print request.FILES 
    file = request.FILES['playlists_data']
    content_compressed = file.read()
    content_uncompressed = zlib.decompress(content_compressed)
    lines = content_uncompressed.split('\n')
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
            playlist = Playlist.objects.create(name=playlist_name, source=source_name)
            print 'playlist created: '
            print playlist
        elif tag == ALBUM_TAG:
            album_name = elements[1]
        elif tag == ARTIST_TAG:
            artist_name = elements[1]
        elif tag == SONG_TAG:
            order = int(elements[1])
            song_name = elements[2]
#            print "song: %(song)s - %(artist)s - %(album)s (%(order)d)" % {"song": song_name, "artist": artist_name, "album": album_name, "order": order}
            metadata = SongMetadata.objects.create(name=song_name, artist_name=artist_name, album_name=album_name)
            song_instance = SongInstance.objects.create(playlist=playlist, metadata=metadata, song=0, order=order, play_count=0, yasound_score=0)
    
    return HttpResponse("You've successfully uploaded playlists to radio '%s'\n" % radio)
