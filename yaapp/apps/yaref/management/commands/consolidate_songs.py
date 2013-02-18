# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from optparse import make_option
from yabase.models import SongMetadata
from yaref.models import YasoundSong
from yaref import utils as yaref_utils
import logging
logger = logging.getLogger("yaapp.yaref")


class Command(BaseCommand):
    """
    """
    option_list = BaseCommand.option_list + (
        make_option('-d', '--dry', dest='dry', action='store_true',
                    default=False, help="dry: does nothing except logging"),
        make_option('-r', '--radio', dest='radio_id',
                    default=0, help="radio id"),
    )
    help = "Consolidate song info from musicbrainz"
    args = ''

    def handle(self, *app_labels, **options):
        dry = options.get('dry', False)
        radio_id = int(options.get('radio_id', 0))

        ids = SongMetadata.objects.filter(songinstance__playlist__radio__id=radio_id,
                                          yasound_song_id__isnull=False).values_list('yasound_song_id', flat=True)
        ids = list(ids)

        songs = YasoundSong.objects.filter(id__in=ids)
        for song in songs:
            if song.musicbrainz_id is not None and len(song.musicbrainz_id) > 2:
                continue
            mbid = yaref_utils.find_track_mbid(song)
            logger.info(u"%s: found %s" % (song, mbid))
            if dry:
                continue
            song.musicbrainz_id = mbid
            song.save()
        logger.info("done")
