# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from optparse import make_option
from time import time
from yabase.models import SongMetadata
from yacore.database import queryset_iterator
from yaref.mongo import SongAdditionalInfosManager
from yaref.models import YasoundSong
from yabase.models import Radio
from yaref import utils as yaref_utils
import datetime
import gc
import logging
import random
import os
logger = logging.getLogger("yaapp.yaref")



class Command(BaseCommand):
    """
    """
    option_list = BaseCommand.option_list + (
        make_option('-d', '--dry', dest='dry', action='store_true',
            default=False, help="dry: does nothing except logging into mongodb"),
        make_option('-r', '--radio', dest='radio_id',
            default=0, help="radio id"),
    )
    help = "Download covers from coverartarchive.org"
    args = ''

    def handle(self, *app_labels, **options):
        dry = options.get('dry', False)
        radio_id = int(options.get('radio_id', 0))

        ids = SongMetadata.objects.filter(songinstance__playlist__radio__id=radio_id, yasound_song_id__isnull=False).values_list('yasound_song_id', flat=True)
        ids = list(ids)

        songs = YasoundSong.objects.filter(id__in=ids, cover_filename__isnull=True, musicbrainz_id__isnull=False)
        for song in songs:
            logger.info("getting cover for %s (%s)" % (song, song.musicbrainz_id))
            data, extension = yaref_utils.find_cover(song.musicbrainz_id)
            if data is None or extension is None:
                continue
            logger.info('found cover for %s' % (song))
            if dry:
                continue
            song.set_cover(data, extension, replace=True)

        logger.info("done")

