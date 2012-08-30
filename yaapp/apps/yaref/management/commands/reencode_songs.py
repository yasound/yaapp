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
            default=False, help="dry: does nothing except logging into mongodb"),
        make_option('-r', '--radio', dest='radio_id',
            default=0, help="radio id"),
        make_option('-n', '--count', dest='radio_count',
            default=0, help="radio count"),
        make_option('-p', '--primary', dest='primary', action='store_true',
            default=False, help="primary: only compute 192k files"),
        make_option('-s', '--song_count', dest='song_count',
            default=100, help="number of songs to compute"),
        make_option('-o', '--random', dest='random', action='store_true',
            default=True, help="randomize songs"),
    )
    help = "Scan songs and check integry on filesystem"
    args = ''

    def handle(self, *app_labels, **options):
        dry = options.get('dry', False)
        radio_id = int(options.get('radio_id', 0))
        radio_count = int(options.get('radio_count', 0))
        song_count = int(options.get('song_count', 0))
        primary = options.get('primary', False)
        rdom = options.get('random', False)

        songs = YasoundSong.objects.all()
        if radio_id > 0:
            yasound_song_ids = list(SongMetadata.objects.filter(songinstance__playlist__radio__id=radio_id).values_list('yasound_song_id', flat=True))
            songs = YasoundSong.objects.filter(id__in=yasound_song_ids)
        if radio_count > 0:
            radios = Radio.objects.filter(ready=True).order_by('?')[:radio_count].values_list('id', flat=True)
            yasound_song_ids = list(SongMetadata.objects.filter(songinstance__playlist__radio__id__in=list(radios)).values_list('yasound_song_id', flat=True))
            songs = YasoundSong.objects.filter(id__in=yasound_song_ids)

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

        sm = SongAdditionalInfosManager()

        global_start = time()
        start = time()
        skipped = 0
        for i, song in enumerate(songs):
            if i % 1000 == 0:
                elapsed = time() - start
                logger.info("processed %d/%d (%s%%) in %s seconds (%d skipped)" % (i, count, 100*i/count, str(elapsed), skipped))
                start = time()

            doc = sm.information(song.id)
            if doc is not None:
                conversion_status = doc.get('conversion_status')
                if conversion_status:
                    if conversion_status.get('high_quality_finished') or conversion_status.get('low_quality_finished') or conversion_status.get('in_progress'):
                        skipped = skipped + 1
                        continue

            async_convert_song.delay(song.id, dry=dry, primary=primary)
        elapsed = time() - global_start
        logger.info("processed %d songs in %s seconds (effective %d)" % (count, str(elapsed), count - skipped))
        logger.info("done")

