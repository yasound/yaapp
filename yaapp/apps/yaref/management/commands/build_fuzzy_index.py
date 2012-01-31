# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from optparse import make_option
from time import time
from yaref.models import YasoundArtist, YasoundAlbum, YasoundSong
import datetime
import gc
from yaref import mongo

import logging
logger = logging.getLogger("yaapp.yaref")


def queryset_iterator(queryset, chunksize=1000):
    '''
    Iterate over a Django Queryset ordered by the primary key

    This method loads a maximum of chunksize (default: 1000) rows in it's
    memory at the same time while django normally would load all rows in it's
    memory. Using the iterator() method only causes it to not preload all the
    classes.

    Note that the implementation of the iterator does not support ordered query sets.
    '''
    pk = 0
    last_pk = queryset.order_by('-pk')[0].pk
    queryset = queryset.order_by('pk')
    while pk < last_pk:
        for row in queryset.filter(pk__gt=pk)[:chunksize]:
            pk = row.pk
            yield row
        gc.collect()

class Command(BaseCommand):
    """
    Update action states
    """
    option_list = BaseCommand.option_list + (
        make_option('-u', '--upsert', dest='upsert', action='store_true',
            default=False, help="upsert : check if document exist before inserting (slow)"),
        make_option('-e', '--erase', dest='erase', action='store_true',
            default=False, help="erase : erase yasound collection and restart indexing from scratch"),
    )
    help = "Generate fuzzy index"
    args = ''

    def handle(self, *app_labels, **options):
        upsert = options.get('upsert',False)
        erase = options.get('erase',False)

        if erase:
            logger.info("deleting index")
            mongo.erase_index()
        
        if upsert:
            logger.info("using upsert")
        else:
            logger.info("not using upsert")
        
        songs = YasoundSong.objects.all()
        last_indexed = YasoundSong.objects.last_indexed()
        if last_indexed:
            logger.info("last indexed = %d" % (last_indexed.id))
            songs = songs.filter(id__gt=last_indexed.id)
        count = songs.count()
        logger.info("processing %d songs" % (count))
        if count > 0:
            start = time()
            if upsert:
                for i, song in enumerate(queryset_iterator(songs)):
                    song.build_fuzzy_index(upsert=True)
                    if i % 10000 == 0:
                        elapsed = time() - start
                        logger.info("processed %d/%d (%d%%) in %s seconds" % (i, count, 100*i/count, str(elapsed)))
                    start = time()
            else:
                bulk = mongo.begin_bulk_insert()
                for i, song in enumerate(queryset_iterator(songs)):
                    bulk.append(song.build_fuzzy_index(upsert=False, insert=False))
                    if i % 10000 == 0:
                        mongo.commit_bulk_insert(bulk)
                        bulk = mongo.begin_bulk_insert()
                        elapsed = time() - start
                        logger.info("processed %d/%d (%d%%) in % seconds" % (i, count, 100*i/count, str(elapsed)))
                        start = time()
        logger.info("building mongodb index")
        mongo.build_index()      
        logger.info("done")
        
