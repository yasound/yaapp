import sys
from celery.task import task
from yabase.models import Radio, Playlist, SongMetadata, SongInstance, YasoundSong, YasoundArtist, YasoundAlbum
import re
from django.db import transaction
from yabase.bulkops import insert_many, update_many
import zlib


class SongImportObject:
    def __init__(self):
        self.playlist = None
        self.artist_name = None
        self.artist_name_simplified = None
        self.album_name = None
        self.album_name_simplified = None
        self.song_name = None
        self.song_name_simplified = None
        self.order = None

        self.metadata = None
        self.instance = None
        self.yasound_song = None

#@transaction.commit_on_success
def get_song_metadatas(objects):
    for object in objects:
        if object.metadata == None:
            try:
                object.metadata = SongMetadata.objects.get(name=object.song_name, artist_name=object.artist_name, album_name=object.album_name)
            except SongMetadata.DoesNotExist:
                0; # do nothing

#@transaction.commit_on_success
def create_song_metadatas(objects):
    operations = []
    for object in objects:
        if object.metadata == None:
            # I use a local object as metadata here as its id will not be updated by the insert_many operation and we'll need to consolidate the list with a new set of "gets":
            metadata = SongMetadata(name=object.song_name, artist_name=object.artist_name, album_name=object.album_name)
            metadata.save()
            operations.append(metadata)
    insert_many(operations)

# Not needed as wee only read:  @transaction.commit_on_success
def get_yasound_songs(objects):
    for object in objects:
        if object.yasound_song == None:
            try:
                #yasound_song = YasoundSong.objects.get(name_simplified=object.song_name_simplified, artist_name_simplified=object.artist_name_simplified, album_name_simplified=object.album_name_simplified)
                songs = YasoundSong.objects.filter(name=object.song_name, artist_name=object.artist_name, album_name=object.album_name)
                object.yasound_song = songs[0]
            except:
                0; # Not found? we can't do anything about it

#@transaction.commit_on_success
def create_song_instances(objects):
    found = 0
    adds = []
    updates = []
    for object in objects:
        try:
            object.song_instance = SongInstance.objects.get(playlist=object.playlist, metadata=object.metadata, order=object.order)
            if object.song_instance.song != object.yasound_song.id:
                object.song_instance.song = object.yasound_song.id
                #object.song_instance.save()
                updates.append(object.song_instance)
        except SongInstance.DoesNotExist:
            if object.yasound_song != None:
                object.song_instance = SongInstance(playlist=object.playlist, metadata=object.metadata, order=object.order, song=object.yasound_song.id)
            else:
                object.song_instance = SongInstance(playlist=object.playlist, metadata=object.metadata, order=object.order)
            #object.song_instance.save()
            adds.append(object.song_instance)
        if object.song_instance.song != None:
            found = found + 1

    insert_many(adds);
    update_many(updates);
    return found

def process_playlists_exec(radio, lines):
    print '*** process_playlists ***'
    PLAYLIST_TAG = 'LIST'
    ARTIST_TAG = 'ARTS'
    ALBUM_TAG = 'ALBM'
    SONG_TAG = 'SONG'

    artist_name = None
    album_name = None
    playlist = None

    pattern = re.compile('[\W_]+')

    count = 0
    found = 0
    notfound = 0

    artist = None;
    album = None;
    song = None;

    objects = [];

    # Parse the input and create a list of SongImportObjects
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
            album_name_simplified = pattern.sub('', album_name).lower()
        elif tag == ARTIST_TAG:
            artist_name = elements[1]
            artist_name_simplified = pattern.sub('', artist_name).lower()
        elif tag == SONG_TAG:
            order = int(elements[1])
            song_name = elements[2]
            song_name_simplified = pattern.sub('', song_name).lower()

            object = SongImportObject()
            object.playlist = playlist
            object.artist_name = artist_name
            object.artist_name_simplified = artist_name_simplified
            object.album_name = album_name
            object.album_name_simplified = album_name_simplified
            object.song_name = song_name
            object.song_name_simplified = song_name_simplified
            object.order = order

            objects.append(object)

    # Get the metadata for each object in the list if they exist:
    print "get_song_metadatas"
    get_song_metadatas(objects)

    # Create the metadata for the objects that did not exist:
    print "create_song_metadatas"
    create_song_metadatas(objects)

    print "update get_song_metadatas"
    get_song_metadatas(objects)

    # Get the songs from the read only song db:
    print "get_yasound_songs"
    get_yasound_songs(objects)

    # Create the song instances:
    print "create_song_instances"
    found = create_song_instances(objects)

    count = len(objects)
    notfount = count - found
    print 'found: %d - not found: %d - total: %d' % (found, notfound, count)



@task
def process_playlists(radio, content_compressed):
    content_uncompressed = zlib.decompress(content_compressed)
    lines = content_uncompressed.split('\n')
    return process_playlists_exec(radio, lines)






