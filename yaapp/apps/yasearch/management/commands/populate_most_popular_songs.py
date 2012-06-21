from django.core.management.base import BaseCommand
from optparse import make_option
from yasearch.models import MostPopularSongsManager
import logging
logger = logging.getLogger("yaapp.yaref")

class Command(BaseCommand):
    """
    Update action states
    """
    option_list = BaseCommand.option_list + (
    )
    help = "Populate most popular songs"
    args = ''

    def handle(self, *app_labels, **options):
        logger.info('populate most popular songs started')
        m = MostPopularSongsManager()
        m.populate()
        logger.info('done')
