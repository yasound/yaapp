# -*- coding: utf-8 -*-
from pymongo import DESCENDING
from django.conf import settings
import utils as yasearch_utils
import settings as yasearch_settings


#
# FIND
#
def find_song(name, album, artist, remove_common_words=True, accurate_album=False):
# from yaref.mongo import *;find_song(u"Voy A Perder La Razón", u"Raíces Del Flamenco (Antología 5)",u"Various Artists, El Agujeta")
    db = settings.MONGO_DB
    dms_name = yasearch_utils.build_dms(name, remove_common_words)
    dms_artist = yasearch_utils.build_dms(artist, remove_common_words)
    dms_album = yasearch_utils.build_dms(album, remove_common_words)

    query_items = []
    if artist and len(dms_artist) > 0:
        query_items.append({"artist_dms":{"$all": dms_artist}})

    if accurate_album:
        album_op = '$all'
    else:
        album_op ='$in'

    if album and len(dms_album) > 0:
        query_items.append({"album_dms":{album_op: dms_album}})

    if name and len(dms_name) > 0:
        query_items.append({"song_dms":{"$all": dms_name}})

    if len(query_items) == 0:
        return []

    res = db.songs.find({"$and":query_items},
                         {
                        "db_id": True,
                        "name": True,
                        "artist": True,
                        "album": True,
                    }).limit(10);
    return res



#
# SEARCH
#

def search_song(search_text, remove_common_words=True, exclude_ids=[]):
    db = settings.MONGO_DB
    dms_search = yasearch_utils.build_dms(search_text, remove_common_words)

    if not search_text or len(dms_search) == 0:
        return []

    res = db.songs.find({ "all_dms":{"$all": dms_search}, "db_id":{"$nin": exclude_ids} },
                         {
                        "db_id": True,
                        "name": True,
                        "artist": True,
                        "album": True,
                    });
    return res



def search_user(search_text, remove_common_words=True):
    db = settings.MONGO_DB
    dms_search = yasearch_utils.build_dms(search_text, remove_common_words)

    if not search_text or len(dms_search) == 0:
        return []

    res = db.users.find({"name_dms":{"$all": dms_search}},
                         {
                        "db_id": True,
                        "name": True,
                    });
    return res
