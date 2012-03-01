from django.db import models
from django.contrib.auth.models import User
#from django.conf import settings
#from fuzzywuzzy import fuzz
from yaref.models import YasoundSong
from yabase.models import Radio
from account.models import UserProfile
import indexer
import logging
from time import time
import utils as yasearch_utils
import indexer as yasearch_indexer
#import yasearch.utils as yasearch_utils
#import string
logger = logging.getLogger("yaapp.yaref")

def build_mongodb_index(upsert=False, erase=False):
    """
    build mongodb fuzzy index : if upsert=False then document is inserted without checking for existent one
    """
    if erase:
        logger.info("deleting index")
        indexer.erase_index()
    
    if upsert:
        logger.info("using upsert")
    else:
        logger.info("not using upsert")

#
#    YasoundSong
#
    songs = YasoundSong.objects.all()
    last_indexed = YasoundSong.objects.last_indexed()
    if last_indexed:
        logger.info("last indexed song = %d" % (last_indexed.id))
        songs = songs.filter(id__gt=last_indexed.id)
    count = songs.count()
    logger.info("processing %d songs" % (count))
    if count > 0:
        start = time()
        if upsert:
            for i, song in enumerate(yasearch_utils.queryset_iterator(songs)):
                song.build_fuzzy_index(upsert=True)
                if i % 10000 == 0 and i != 0:
                    elapsed = time() - start
                    logger.info("processed %d/%d (%d%%) songs in %s seconds" % (i+1, count, 100*i/count, str(elapsed)))
                    start = time()
        else:
            bulk = indexer.begin_bulk_insert()
            for i, song in enumerate(yasearch_utils.queryset_iterator(songs)):
                bulk.append(song.build_fuzzy_index(upsert=False, insert=False))
                if i % 10000 == 0 and i != 0:
                    indexer.commit_bulk_insert_songs(bulk)
                    bulk = indexer.begin_bulk_insert()
                    elapsed = time() - start
                    logger.info("processed %d/%d (%d%%) songs in % seconds" % (i+1, count, 100*i/count, str(elapsed)))
                    start = time()
            indexer.commit_bulk_insert_songs(bulk)
            elapsed = time() - start
            logger.info("processed %d/%d (%d%%) songs in % seconds" % (count, count, 100, str(elapsed)))

#
#    Radio
#
    radios = Radio.objects.all()
    last_indexed = Radio.objects.last_indexed()
    if last_indexed:
        logger.info("last indexed radio = %d" % (last_indexed.id))
        radios = radios.filter(id__gt=last_indexed.id)
    count = radios.count()
    logger.info("processing %d radios" % (count))
    if count > 0:
        start = time()
        if upsert:
            for i, radio in enumerate(yasearch_utils.queryset_iterator(radios)):
                radio.build_fuzzy_index(upsert=True)
                if i % 10000 == 0 and i != 0:
                    elapsed = time() - start
                    logger.info("processed %d/%d (%d%%) radios in %s seconds" % (i+1, count, 100*i/count, str(elapsed)))
                    start = time()
        else:
            bulk = indexer.begin_bulk_insert()
            for i, radio in enumerate(yasearch_utils.queryset_iterator(radios)):
                bulk.append(radio.build_fuzzy_index(upsert=False, insert=False))
                if i % 10000 == 0 and i != 0:
                    indexer.commit_bulk_insert_radios(bulk)
                    bulk = indexer.begin_bulk_insert()
                    elapsed = time() - start
                    logger.info("processed %d/%d (%d%%) radios in % seconds" % (i+1, count, 100*i/count, str(elapsed)))
                    start = time()
            indexer.commit_bulk_insert_radios(bulk)
            elapsed = time() - start
            logger.info("processed %d/%d (%d%%) radios in % seconds" % (count, count, 100, str(elapsed)))
            
#
#    User
#
    users = User.objects.all()
#    last_indexed = UserProfile.objects.last_indexed_user()
    doc = yasearch_indexer.get_last_user_doc()
    last_indexed = None
    if doc and doc.count() > 0:
        last_indexed = User.objects.get(id=doc[0]['db_id']) 
    
    if last_indexed:
        logger.info("last indexed user = %d" % (last_indexed.id))
        users = users.filter(id__gt=last_indexed.id)
    count = users.count()
    logger.info("processing %d users" % (count))
    if count > 0:
        start = time()
        if upsert:
            for i, user in enumerate(yasearch_utils.queryset_iterator(users)):
                user.userprofile.build_fuzzy_index(upsert=True)
                if i % 10000 == 0 and i != 0:
                    elapsed = time() - start
                    logger.info("processed %d/%d (%d%%) users in %s seconds" % (i+1, count, 100*i/count, str(elapsed)))
                    start = time()
        else:
            bulk = indexer.begin_bulk_insert()
            for i, user in enumerate(yasearch_utils.queryset_iterator(users)):
                bulk.append(user.userprofile.build_fuzzy_index(upsert=False, insert=False))
                if i % 10000 == 0 and i != 0:
                    indexer.commit_bulk_insert_users(bulk)
                    bulk = indexer.begin_bulk_insert()
                    elapsed = time() - start
                    logger.info("processed %d/%d (%d%%) users in % seconds" % (i+1, count, 100*i/count, str(elapsed)))
                    start = time()
            indexer.commit_bulk_insert_users(bulk)
            elapsed = time() - start
            logger.info("processed %d/%d (%d%%) users in % seconds" % (count, count, 100, str(elapsed)))
    
    
    logger.info("building mongodb index")
    indexer.build_index_songs() 
    indexer.build_index_radios() 
    indexer.build_index_users()      
    logger.info("done")
    
    
    
    
    
def search_radio(search_text, radio_min_score=40):
        radio_results = Radio.objects.search_fuzzy(search_text, 5)
        radios = []
        for r in radio_results:
            radio_id = r[0]["db_id"]
            score = r[1]
            if score >= radio_min_score:
                radios.append(Radio.objects.get(id=radio_id))
            else:
                break
        return radios
    
def search_radio_by_user(search_text, user_min_score=50):
        user_results = UserProfile.objects.search_user_fuzzy(search_text, 5)
        users = []
        for u in user_results:
            user_id = u[0]["db_id"]
            score = u[1]
            if score >= user_min_score:
                users.append(User.objects.get(id=user_id))
            else:
                break
        radios = []
        for u in users:
            if u.userprofile.own_radio and u.userprofile.own_radio.ready:
                radios.append(u.userprofile.own_radio)
        return radios
    
def search_radio_by_song(search_text, limit=10):
        song_results = YasoundSong.objects.search_fuzzy(search_text, 1000)
        songs = []
        for s in song_results:
            songs.append(s[0]["db_id"])
        radios = Radio.objects.filter(current_song__metadata__yasound_song_id__in=songs).order_by('-overall_listening_time')[:limit]
        return radios
    
    
    