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
from yabase.models import SongInstance
logger = logging.getLogger("yaapp.yabase")


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
        make_option('-d', '--dry', dest='dry', action='store_true',
            default=False, help="dry: does nothing"),
        make_option('-r', '--reindex', dest='reindex', action='store_true',
            default=False, help="reindex: check for already associated song_instances"),
    )
    help = "Scan song instance to create a link with yasound songs"
    args = ''

    def handle(self, *app_labels, **options):
        dry = options.get('dry', False)
        reindex = options.get('reindex', False)

        song_instances = SongInstance.objects.all().select_related();
        count = song_instances.count()
        logger.info("processing %d song instances" % (count))
        
        found, not_found = 0, 0
        if count > 0:
            global_start = time()
            start = time()
            for i, song_instance in enumerate(queryset_iterator(song_instances)):
                if song_instance.song and not reindex:
                    logger.debug("skipping %s|%s|%s because song_id = %d" % (song_instance.metadata.name,
                                               song_instance.metadata.album_name,
                                               song_instance.metadata.artist_name,
                                               song_instance.song))
                    continue;
                doc = YasoundSong.objects.find_fuzzy(song_instance.metadata.name,
                                               song_instance.metadata.album_name,
                                               song_instance.metadata.artist_name)
                if doc:
                    found +=1
                    song_instance.song = doc['db_id']
                    if not dry:
                        song_instance.save()
                else:
                    not_found +=1
                if i % 1000 == 0:
                    elapsed = time() - start
                    logger.info("processed %d/%d (%d%%) in %s seconds, %d found, %d not found" % (i, count, 100*i/count, str(elapsed), found, not_found))
                    start = time()
            elapsed = time() - global_start
            logger.info("processed %d songs in %s seconds, %d found, %d not found" % (count, str(elapsed), found, not_found))
        logger.info("done")
        
