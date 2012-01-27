# -*- coding: utf-8 -*-

from pymongo import ASCENDING, DESCENDING
from django.conf import settings
import metaphone
import settings as yaref_settings
import string

exclude = set(string.punctuation)

def _remove_punctuation(s):
    return ''.join(ch for ch in s if ch not in exclude)
    
def _build_dms(sentence, remove_common_words=False):
    dms = []
    if not sentence:
        return dms
    sentence = _remove_punctuation(sentence)
    words = sorted(sentence.lower().split())
    for word in words:
        if remove_common_words and (word in yaref_settings.FUZZY_COMMON_WORDS or len(word) < 3):
            continue 
        dm = metaphone.dm(word)
        value = u'%s - %s' % (dm[0], dm[1])
        if value == u' - ':
            continue
        if value not in dms:
            dms.append(value)
    return dms

def build_index():
    db = settings.MONGO_DB
    db.songs.ensure_index("song_dms")
    db.songs.ensure_index("artist_dms")
    db.songs.ensure_index("album_dms")
    

def add_song(song, upsert=False):
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
    if upsert:
        db.songs.update({"db_id": song.id},
                        {"$set": song_doc}, upsert=True, safe=True)
    else:
        db.songs.insert(song_doc, safe=True)
        
def find_song(name, album, artist):
# from yaref.mongo import *;find_song(u"Voy A Perder La Razón", u"Raíces Del Flamenco (Antología 5)",u"Various Artists, El Agujeta")
    db = settings.MONGO_DB
    dms_name = _build_dms(name, remove_common_words=True)
    dms_artist = _build_dms(artist, remove_common_words=True)
    dms_album = _build_dms(album, remove_common_words=True)
    
    res = db.songs.find({"song_dms":{"$all": dms_name},
                   "artist_dms":{"$all": dms_artist},
                   "album_dms":{"$all": dms_album},
                   }, {
                        "db_id": True,
                        "name": True,
                        "artist": True,
                        "album": True,
                    });
    return res

def get_last_doc():
    db = settings.MONGO_DB
    return db.songs.find().sort([("$natural", DESCENDING)]).limit(1)
