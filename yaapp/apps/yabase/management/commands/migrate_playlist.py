from django.core.management.base import BaseCommand
from optparse import make_option
from yabase.models import Playlist
import logging

logger = logging.getLogger("yaapp.yabase")

class Command(BaseCommand):
    """
    Move songinstance from playlist to another
    """
    option_list = BaseCommand.option_list + (
        make_option('-d', '--dry', dest='dry', action='store_true',
            default=False, help="dry: does nothing"),
    )
    help = "Move songinstance from playlist to another"
    args = ''

    def handle(self, *app_labels, **options):
        dry = options.get('dry', False)

        Playlist.objects.migrate_songs_to_default(dry)

        logger.info("done")
        
