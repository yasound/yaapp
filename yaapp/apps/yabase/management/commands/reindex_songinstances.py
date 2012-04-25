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


from yacore.database import queryset_iterator


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
        
        found, not_found, skipped = 0, 0, 0
        if count > 0:
            global_start = time()
            start = time()
            for i, song_instance in enumerate(queryset_iterator(song_instances)):
                if song_instance.song and not reindex:
                    skipped += 1
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
                    logger.info("processed %d/%d (%d%%) in %s seconds, %d found, %d not found, %d skipped" % (i, count, 100*i/count, str(elapsed), found, not_found, skipped))
                    start = time()
            elapsed = time() - global_start
            logger.info("processed %d songs in %s seconds, %d found, %d not found, %d skipped" % (count, str(elapsed), found, not_found, skipped))
        logger.info("done")
        
