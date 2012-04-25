from django.core.management.base import BaseCommand
from optparse import make_option
from yabase import task
from yabase.models import Playlist, Radio, SongMetadata
from yaref.models import YasoundSong
from yacore.database import queryset_iterator
import logging


logger = logging.getLogger("yaapp.yabase")

class Command(BaseCommand):
    """
    Extract covers
    """
    option_list = BaseCommand.option_list + (
        make_option('-d', '--dry', dest='dry', action='store_true',
            default=False, help="dry: does nothing"),
        make_option('-s', '--start', dest='start_id',
            default=0, help="yasound song instance id to start"),
        make_option('-r', '--radio', dest='radio_id',
            default=0, help="radio id"),
    )
    help = "Extract cover"
    args = ''

    def handle(self, *app_labels, **options):
        dry = options.get('dry', False)
        start_id = int(options.get('start_id', 0))
        radio_id = int(options.get('radio_id', 0))

        logger.info("start id = %d" % (start_id))
        
        if not radio_id and start_id > 0:
            songs = YasoundSong.objects.filter(id__gt=start_id, cover_filename__isnull=True)
            count = songs.count()
            logger.info("processing %d songs" % (count))
            if count <= 0:
                return
            
            for song in queryset_iterator(songs):
                if dry:
                    continue
                task.extract_song_cover.delay(song.id)
        
        if radio_id:
            radio = Radio.objects.get(id=radio_id)
            logger.info("radio id = %d (%s) "  % (radio_id, radio))
            
            ids = SongMetadata.objects.filter(songinstance__playlist__radio=radio).values_list('yasound_song_id', flat=True)
            songs = YasoundSong.objects.filter(id__in=list(ids), cover_filename__isnull=True)
            count = songs.count()
            logger.info("processing %d songs" % (count))
            for song in songs:
                if dry:
                    continue
                task.extract_song_cover.delay(song.id)
        
        logger.info("done")        
        
        
