import sys
from celery.task import task
from yabase.models import Radio, Playlist, SongMetadata, SongInstance, YasoundSong, YasoundArtist, YasoundAlbum
import re
from django.db import transaction
from yabase.bulkops import insert_many, update_many
import zlib
from struct import *
import time

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

@transaction.commit_on_success
def get_song_metadatas(objects):
    print "get_song_metadatas"
    t = time.time()
    ok = 0
    nok = 0
    for object in objects:
        if object.metadata == None:
            #metadata = SongMetadata.objects.get(name=object.song_name, artist_name=object.artist_name, album_name=object.album_name)
            raw = SongMetadata.objects.raw("SELECT * from yabase_songmetadata WHERE name=%s and artist_name=%s and album_name=%s",
                                           [object.song_name,
                                            object.artist_name,
                                            object.album_name])
            for item in raw:
                object.metadata = item
                ok = ok + 1
                break
            else:
                nok = nok + 1
    t = time.time() - t
    print ' ( ' + str(ok) + ' / ' + str(nok + ok) + ')'
    print ' -> ' + str(t) + ' s'


@transaction.commit_on_success
def create_song_metadatas(objects):
    print "create_song_metadatas"
    t = time.time()
    operations = []
    md = set([])
    for object in objects:
        if object.metadata == None:
            # I use a local object as metadata here as its id will not be updated by the insert_many operation and we'll need to consolidate the list with a new set of "gets":
            hash = object.song_name + '|' + object.artist_name + '|' + object.album_name;
            if hash not in md:
                metadata = SongMetadata(name=object.song_name, artist_name=object.artist_name, album_name=object.album_name)
                md.add(hash)
                #metadata.save()
                operations.append(metadata)
    insert_many(operations)
    t = time.time() - t
    print " -> " + str(t) + ' s'

@transaction.commit_on_success
def get_yasound_songs(objects):
    print "get_yasound_songs"
    t = time.time()
    for object in objects:
        if object.yasound_song == None:
            raw = YasoundSong.objects.raw("SELECT * from yasound_song WHERE name=%s and artist_name=%s and album_name=%s",
                                           [object.song_name,
                                            object.artist_name,
                                            object.album_name])
            for item in raw:
                object.yasound_song = item.id
                break
    t = time.time() - t
    print " -> " + str(t) + ' s'




@transaction.commit_on_success
def old_create_song_instances(objects):
    print "create_song_instances"
    t = time.time()
    found = 0
    adds = []
    updates = []
    for object in objects:
        try:
            instance = SongInstance.objects.get(playlist=object.playlist, metadata=object.metadata, order=object.order)
            if instance.song != object.yasound_song:
                instance.song = object.yasound_song
                #object.song_instance.save()
                updates.append(instance)
        except SongInstance.DoesNotExist:
            if object.yasound_song != None:
                instance = SongInstance(playlist=object.playlist, metadata=object.metadata, order=object.order, song=object.yasound_song)
            else:
                instance = SongInstance(playlist=object.playlist, metadata=object.metadata, order=object.order)
            #object.song_instance.save()
            adds.append(instance)
        if instance.song != None:
            found = found + 1

    insert_many(adds);
    update_many(updates);

    t = time.time() - t
    print " -> " + str(t) + ' s'
    return found

@transaction.commit_on_success
def create_song_instances(objects):
    print "create_song_instances"
    t = time.time()
    found = 0
    adds = []
    updates = []
    for object in objects:
        res = SongInstance.objects.filter(playlist=object.playlist, metadata=object.metadata, order=object.order)
        done = False
        for item in res:
            if (item.song != object.yasound_song):
                item.song = object.yasound_song
                updates.append(item)
                found = found + 1
                done = True
            break
        if not done:
            if object.yasound_song != None:
                adds.append(SongInstance(playlist=object.playlist, metadata=object.metadata, order=object.order, song=object.yasound_song))
            else:
                adds.append(SongInstance(playlist=object.playlist, metadata=object.metadata, order=object.order))

    insert_many(adds);
    update_many(updates);

    t = time.time() - t
    print " -> " + str(t) + ' s'
    return found

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

#@transaction.commit_on_success
def process_playlists_exec(radio, content_compressed):
    print "decompress playlist"
    content_uncompressed = zlib.decompress(content_compressed)

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
    data = BinaryData(content_uncompressed)

    while not data.is_done():
        tag = data.get_tag()

        if tag == PLAYLIST_TAG:
            playlist_name = data.get_string()
            source_name = 'test_playlist_file'
            playlist, created = Playlist.objects.get_or_create(name=playlist_name, source=source_name)
            if created:
                print 'playlist created '
                print playlist
            else:
                print 'playlist found '
                print playlist

        elif tag == ALBUM_TAG:
            album_name = data.get_string()
            album_name_simplified = pattern.sub('', album_name).lower()
        elif tag == ARTIST_TAG:
            artist_name = data.get_string()
            artist_name_simplified = pattern.sub('', artist_name).lower()
        elif tag == SONG_TAG:
            order = data.get_int32()
            song_name = data.get_string()
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
    get_song_metadatas(objects)

    # Create the metadata for the objects that did not exist:
    create_song_metadatas(objects)

    get_song_metadatas(objects)

    # Get the songs from the read only song db:
    get_yasound_songs(objects)

    # Create the song instances:
    found = create_song_instances(objects)

    count = len(objects)
    notfount = count - found
    print 'found: %d - not found: %d - total: %d' % (found, notfound, count)



@task
def process_playlists(radio, content_compressed):
    return process_playlists_exec(radio, content_compressed)






