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
    Move song attribute (YasoundSong.id) from SongInstance to SongMetadata)
    """
    option_list = BaseCommand.option_list + (
        make_option('-d', '--dry', dest='dry', action='store_true',
            default=False, help="dry: does nothing"),
    )
    help = "Move song attribute (YasoundSong.id) from SongInstance to SongMetadata)"
    args = ''

    def handle(self, *app_labels, **options):
        dry = options.get('dry', False)

        song_instances = SongInstance.objects.filter(song__isnull=False).select_related();
        count = song_instances.count()
        logger.info("processing %d song instances" % (count))
        
        if count > 0:
            global_start = time()
            start = time()
            for i, song_instance in enumerate(queryset_iterator(song_instances)):
                if dry:
                    continue
                song_instance.metadata.yasound_song_id = song_instance.song
                song_instance.metadata.save()
                song_instance.song = None
                song_instance.save()
                if i % 1000 == 0:
                    elapsed = time() - start
                    logger.info("processed %d/%d (%d%%) in %s seconds" % (i, count, 100*i/count, str(elapsed)))
                    start = time()
            elapsed = time() - global_start
            logger.info("processed %d songs in %s seconds" % (count, str(elapsed)))
        logger.info("done")
        
