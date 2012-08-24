# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from optparse import make_option
from time import time
from yabase.models import SongMetadata
from yacore.database import queryset_iterator
from yaref import mongo
from yaref.models import YasoundSong
import datetime
import gc
import logging
import os
from yaref.task import async_convert_song
logger = logging.getLogger("yaapp.yaref")



class Command(BaseCommand):
    """
    Re-encode songs
    """
    option_list = BaseCommand.option_list + (
        make_option('-d', '--dry', dest='dry', action='store_true',
            default=False, help="dry: does nothing except logging into mongodb"),
        make_option('-r', '--radio', dest='radio_id',
            default=0, help="radio id"),
    )
    help = "Scan songs and check integry on filesystem"
    args = ''

    def handle(self, *app_labels, **options):
        dry = options.get('dry', False)
        radio_id = int(options.get('radio_id', 0))
        songs = YasoundSong.objects.all()
        if radio_id > 0:
            yasound_song_ids = list(SongMetadata.objects.filter(songinstance__playlist__radio__id=radio_id).values_list('yasound_song_id', flat=True))
            songs = YasoundSong.objects.filter(id__in=yasound_song_ids)
        count = songs.count() 
        logger.info("processing %d song instances" % (count))
        
        if count == 0:
            return
        
        global_start = time()
        start = time()
        for i, song in enumerate(queryset_iterator(songs)):
            async_convert_song.delay(song.id, dry=dry)
            if i % 1000 == 0:
                elapsed = time() - start
                logger.info("processed %d/%d (%d%%) in %s seconds" % (i, count, 100*i/count, str(elapsed)))
                start = time()
        elapsed = time() - global_start
        logger.info("processed %d songs in %s seconds" % (count, str(elapsed)))
        logger.info("done")
        
