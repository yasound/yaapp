from django.core.management.base import BaseCommand
from optparse import make_option
from yabase.models import Playlist
from yaref.models import YasoundSong
from yaref.utils import queryset_iterator
import logging

from yabase import task

logger = logging.getLogger("yaapp.yaref")

class Command(BaseCommand):
    """
    Generate mp3 preview
    """
    option_list = BaseCommand.option_list + (
        make_option('-d', '--dry', dest='dry', action='store_true',
            default=False, help="dry: does nothing"),
        make_option('-s', '--start', dest='start_id',
            default=0, help="song instance id to start"),
    )
    help = "Move songinstance from playlist to another"
    args = ''

    def handle(self, *app_labels, **options):
        dry = options.get('dry', False)
        start_id = int(options.get('start_id', 0))
        
        logger.info("start id = %d" % (start_id))
        songs = YasoundSong.objects.filter(id__gt=start_id)
        count = songs.count()
        logger.info("processing %d songs" % (count))
        if count <= 0:
            return
        
        for song in queryset_iterator(songs):
            task.generate_preview.delay(song.id)
            
        
        
