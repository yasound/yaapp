# -*- coding: utf-8 -*-
from pymongo import DESCENDING
from django.conf import settings
import utils as yasearch_utils
import settings as yasearch_settings

def begin_bulk_insert():
    return []

def build_index_songs():
    db = settings.MONGO_DB
    db.songs.ensure_index("song_dms")
    db.songs.ensure_index("artist_dms")
    db.songs.ensure_index("album_dms")
    db.songs.ensure_index("all_dms")

def build_index_users():
    db = settings.MONGO_DB
    db.users.ensure_index("db_id")
    db.users.ensure_index("name_dms")
    db.users.ensure_index("all_dms")



def commit_bulk_insert_songs(data):
    db = settings.MONGO_DB
    if len(data) > 0:
        db.songs.insert(data, safe=True)

def commit_bulk_insert_radios(data):
    db = settings.MONGO_DB
    if len(data) > 0:
        db.radios.insert(data, safe=True)

def commit_bulk_insert_users(data):
    db = settings.MONGO_DB
    if len(data) > 0:
        db.users.insert(data, safe=True)

#
# ADD
#
def add_song(song, upsert=False, insert=True):
    song_dms = yasearch_utils.build_dms(song.name, True, yasearch_settings.SONG_STRING_EXCEPTIONS)
    artist_dms = yasearch_utils.build_dms(song.artist_name, True, yasearch_settings.SONG_STRING_EXCEPTIONS)
    album_dms =  yasearch_utils.build_dms(song.album_name, True, yasearch_settings.SONG_STRING_EXCEPTIONS)

    all_dms = []
    all_dms.extend(song_dms)
    all_dms.extend(artist_dms)
    all_dms.extend(album_dms)
    all_dms = list(set(all_dms))

    song_doc = {
        "db_id": song.id,
        "name": song.name,
        "artist": song.artist_name,
        "album": song.album_name,
        "song_dms": song_dms,
        "artist_dms": artist_dms,
        "album_dms": album_dms,
        "all_dms": all_dms,
    }
    if upsert:
        db = settings.MONGO_DB
        db.songs.update({"db_id": song.id},
                        {"$set": song_doc}, upsert=True, safe=True)
    elif insert:
        db = settings.MONGO_DB
        db.songs.insert(song_doc, safe=True)
    return song_doc

def add_user(user, upsert=False, insert=True):
    user_doc = {
        "db_id": user.id,
        "name": user.userprofile.name,
        "name_dms": yasearch_utils.build_dms(user.get_profile().name, True),
    }
    if upsert:
        db = settings.MONGO_DB
        db.users.update({"db_id": user.id},
                        {"$set": user_doc}, upsert=True, safe=True)
    elif insert:
        db = settings.MONGO_DB
        db.users.insert(user_doc, safe=True)

    return user_doc

def remove_user(user):
    db = settings.MONGO_DB
    docs = db.users.find({"db_id": user.id}).limit(1)
    if docs and docs.count() > 0:
        doc = docs[0]
        db.users.remove({'_id': doc['_id']})

def get_last_song_doc():
    db = settings.MONGO_DB
    return db.songs.find().sort([("$natural", DESCENDING)]).limit(1)

def get_last_user_doc():
    db = settings.MONGO_DB
    return db.users.find().sort([("db_id", DESCENDING)]).limit(1)

def erase_index(skip_songs=False):
    db = settings.MONGO_DB
    if not skip_songs:
        db.songs.drop()
    db.radios.drop()
    db.users.drop()