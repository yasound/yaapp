# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from optparse import make_option
from time import time
import datetime
import gc
from yaref import mongo

import logging
from yaref.models import YasoundSong
logger = logging.getLogger("yaapp.yaref")
import os

from yacore.database import queryset_iterator


class Command(BaseCommand):
    """
    Check state of songs on filesystem
    """
    option_list = BaseCommand.option_list + (
        make_option('-s', '--start_id', dest='start_id',
            default=0, help="start id"),
    )
    help = "Scan songs and check integry on filesystem"
    args = ''

    def handle(self, *app_labels, **options):
        start_id = int(options.get('start_id', 0))
        if start_id > 0:
            songs = YasoundSong.objects.filter(id__gte=start_id)
        else:
            songs = YasoundSong.objects.all()
        count = songs.count() 
        logger.info("processing %d song instances" % (count))
        
        if count == 0:
            return
        
        global_start = time()
        start = time()
        for i, song in enumerate(queryset_iterator(songs)):
            song_path = song.get_song_path()
            if not os.path.exists(song_path):
                logger.error('%d : song file does not exists : %s' % (song.id, song_path))

            song_preview_path = song.get_song_preview_path()
            if not os.path.exists(song_preview_path):
                logger.error('%d : song preview file does not exists : %s' % (song.id, song_preview_path))
            
            if i % 1000 == 0:
                elapsed = time() - start
                logger.info("processed %d/%d (%d%%) in %s seconds" % (i, count, 100*i/count, str(elapsed)))
                start = time()
        elapsed = time() - global_start
        logger.info("processed %d songs in %s seconds" % (count, str(elapsed)))
        logger.info("done")
        
