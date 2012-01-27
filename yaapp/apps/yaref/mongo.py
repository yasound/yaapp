from django.conf import settings
import metaphone

def _build_dms(sentence):
    dms = []
    words = sentence.lower().split()
    for word in words:
        dm = metaphone.dm(word)
        value = u'%s - %s' % (dm[0], dm[1])
        dms.append(value)
    return dms

def add_song(song):
    db = settings.MONGO_DB
    song_doc = {
        "db_id": song.id,
        "name": song.name,
        "artist": song.artist_name,
        "album": song.album_name,
        "song_dms": _build_dms(song.name),
        "artist_dms": _build_dms(song.artist_name),
        "album_dms": _build_dms(song.album_name),
    }
    db.songs.update({"db_id": song.id},
                    {"$set": song_doc}, upsert=True, safe=True)
    
def find_song(name, album, artist):
    db = settings.MONGO_DB
    dms_name = _build_dms(name)
    dms_artist = _build_dms(artist)
    dms_album = _build_dms(album)
    
    res = db.songs.find({"song_dms":{"$in": dms_name},
                   "artist_dms":{"$in": dms_artist},
                   "album_dms":{"$in": dms_album},
                   });
    return res    