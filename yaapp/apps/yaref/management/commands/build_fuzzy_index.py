from django.core.management.base import BaseCommand
from optparse import make_option
from yaref import models
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
    )
    help = "Generate fuzzy index"
    args = ''

    def handle(self, *app_labels, **options):
        upsert = options.get('upsert',False)
        erase = options.get('erase',False)
        models.build_mongodb_index(upsert=upsert, erase=erase)
