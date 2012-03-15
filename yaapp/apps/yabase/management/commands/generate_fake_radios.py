from django.core.management.base import BaseCommand
from optparse import make_option
from yabase import task
from yabase.models import Playlist, Radio, SongMetadata
from yaref.models import YasoundSong
from yaref.utils import queryset_iterator
import logging

from yabase.models import Radio
logger = logging.getLogger("yaapp.yabase")

class Command(BaseCommand):
    """
    Generate mp3 preview
    """
    option_list = BaseCommand.option_list + (
        make_option('-D', '--delete', dest='delete_radios', action='store_true',
            default=0, help="delete all fake radios"),
        make_option('-m', '--max', dest='radio_count',
            default=50, help="number of radios (default=50)"),
    )
    help = "Generate fake radios"
    args = ''

    def handle(self, *app_labels, **options):
        radio_count = int(options.get('radio_count', 50))
        delete_radios = options.get('delete_radios', False)

        if delete_radios:
            logger.info("deleting radios")
            Radio.objects.delete_fake_radios()
        else:
            logger.info("generating fake radios")
            Radio.objects.generate_fake_radios(radio_count)
        logger.info("done")
        
        
