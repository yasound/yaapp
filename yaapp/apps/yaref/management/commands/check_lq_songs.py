# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from optparse import make_option
from time import time
from yabase.models import SongMetadata
from yacore.database import queryset_iterator
from yaref.mongo import SongAdditionalInfosManager
from yaref.models import YasoundSong
from yabase.models import Radio
import datetime
import gc
import logging
import random
import os
from yaref.task import async_convert_song
logger = logging.getLogger("yaapp.yaref")


class Command(BaseCommand):
    """
    Re-encode songs
    """
    option_list = BaseCommand.option_list + (
        make_option('-d', '--dry', dest='dry', action='store_true',
                    default=False, help="dry: does nothing"),
        make_option('-s', '--song_count', dest='song_count',
                    default=100, help="number of songs to compute"),
        make_option('-o', '--random', dest='random', action='store_true',
                    default=False, help="randomize songs"),
    )
    help = "Scan songs and check integry on filesystem"
    args = ''

    def handle(self, *app_labels, **options):
        dry = options.get('dry', False)
        song_count = int(options.get('song_count', 0))
        rdom = options.get('random', False)

        songs = YasoundSong.objects.all()

        count = songs.count()

        if rdom:
            ids = []
            for i in range(0, song_count):
                ids.append(random.randrange(1, count))
                songs = YasoundSong.objects.filter(id__in=ids)

        count = songs.count()
        logger.info("processing %d song instances" % (count))

        if count == 0:
            return

        global_start = time()
        start = time()
        skipped = 0
        for i, song in enumerate(songs):
            if i % 1000 == 0:
                elapsed = time() - start
                logger.info(
                    "processed %d/%d (%s%%) in %s seconds (%d skipped)" % (i, count, 100 * i / count, str(elapsed), skipped))
                start = time()
            if song.lq_file_exists():
                skipped = skipped + 1
                continue
            if not song.file_exists():
                logger.info('no file for %s (%s)' % (song, song.id))
                continue
            logger.info('processing %s (%s)' % (song, song.id))
            if dry:
                continue
            song.generate_low_quality()
        elapsed = time() - global_start
        logger.info("processed %d songs in %s seconds (effective %d)" % (count, str(elapsed), count - skipped))
        logger.info("done")
