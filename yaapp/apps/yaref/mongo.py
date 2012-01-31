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
        if remove_common_words and (word in yaref_settings.FUZZY_COMMON_WORDS):
            continue 
        if word.isdigit():
            value = word
        else:
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
    
def begin_bulk_insert():
    return []

def commit_bulk_insert(data):
    db = settings.MONGO_DB
    db.songs.insert(data, safe=True)
        
def add_song(song, upsert=False, insert=True):
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
        db = settings.MONGO_DB
        db.songs.update({"db_id": song.id},
                        {"$set": song_doc}, upsert=True, safe=True)
    elif insert:
        db = settings.MONGO_DB
        db.songs.insert(song_doc, safe=True)
    return song_doc

def find_song(name, album, artist, remove_common_words=True):
# from yaref.mongo import *;find_song(u"Voy A Perder La Razón", u"Raíces Del Flamenco (Antología 5)",u"Various Artists, El Agujeta")
    db = settings.MONGO_DB
    dms_name = _build_dms(name, remove_common_words)
    dms_artist = _build_dms(artist, remove_common_words)
    dms_album = _build_dms(album, remove_common_words)
    
    query_items = []
    if name and len(dms_name) > 0:
        query_items.append({"song_dms":{"$all": dms_name}})

    if artist and len(dms_artist) > 0:
        query_items.append({"artist_dms":{"$all": dms_artist}})

    if album and len(dms_album) > 0:
        query_items.append({"album_dms":{"$all": dms_album}})

    res = db.songs.find({"$and":query_items}, 
                         {
                        "db_id": True,
                        "name": True,
                        "artist": True,
                        "album": True,
                    }).limit(10);
    return res

def get_last_doc():
    db = settings.MONGO_DB
    return db.songs.find().sort([("$natural", DESCENDING)]).limit(1)

def erase_index():
    db = settings.MONGO_DB
    db.songs.drop()