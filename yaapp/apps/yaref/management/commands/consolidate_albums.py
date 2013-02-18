# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from optparse import make_option
from yabase.models import SongMetadata
from yaref.models import YasoundSong, YasoundAlbum
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
    help = "Consolidate missing albums from musicbrainz"
    args = ''

    def handle(self, *app_labels, **options):
        dry = options.get('dry', False)
        radio_id = int(options.get('radio_id', 0))
        print "radio id = %d" % (radio_id)
        ids = SongMetadata.objects.filter(songinstance__playlist__radio__id=radio_id).values_list('yasound_song_id', flat=True)
        ids = list(ids)

        songs = YasoundSong.objects.filter(id__in=ids)
        logger.info(u"%d radio count" % (songs.count()))
        for song in songs:
            if song.musicbrainz_id is None or len(song.musicbrainz_id) < 2:
                logger.info(u"%s (%s): skipping (musicbrainz does not exists)" % (song, song.musicbrainz_id))
                continue
            if song.album is not None:
                logger.info(u"%s (%s): skipping (album exists)" % (song, song.musicbrainz_id))
                continue
            logger.info(u"%s (%s): trying to find album" % (song, song.musicbrainz_id))
            album = yaref_utils.generate_album(song.musicbrainz_id)
            if dry:
                continue

            if album is not None and YasoundAlbum.objects.filter(musicbrainz_id=album.musicbrainz_id).count() == 0:
                logger.info(u"%s (%s): generating album (%s)" % (song, song.musicbrainz_id, album))
                album.save()
                song.album = album
                song.save()

                data, extension = yaref_utils.find_cover(song.album.musicbrainz_id)
                if data is None or extension is None:
                    continue
                logger.info(u"%s (%s): found cover" % (song, song.musicbrainz_id))
                song.album.set_cover(data, extension, replace=False)
        logger.info("done")
