from django.core.management.base import BaseCommand
from optparse import make_option
from yasearch import models as yasearch_models
import logging
logger = logging.getLogger("yaapp.yaref")

class Command(BaseCommand):
    """
    Update action states
    """
    option_list = BaseCommand.option_list + (
        make_option('-u', '--upsert', dest='upsert', action='store_true',
            default=False, help="upsert : check if document exist before inserting (slow)"),
        make_option('-e', '--erase', dest='erase', action='store_true',
            default=False, help="erase : erase yasound collection and restart indexing from scratch"),
        make_option('-s', '--skip-songs', dest='skip_songs', action='store_true',
            default=False, help="skip-songs: does not touch songs index"),
    )
    help = "Generate fuzzy index"
    args = ''

    def handle(self, *app_labels, **options):
        upsert = options.get('upsert',False)
        erase = options.get('erase',False)
        skip_songs = options.get('skip_songs', False)
        yasearch_models.build_mongodb_index(upsert=upsert, erase=erase, skip_songs=skip_songs)
