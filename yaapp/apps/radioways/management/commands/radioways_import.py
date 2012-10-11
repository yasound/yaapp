# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from optparse import make_option
from time import time
import datetime
import gc
from yaref import mongo

import logging
from yaref.models import YasoundSong
logger = logging.getLogger("yaapp.radioways")
import os
from radioways.import_utils import *


class Command(BaseCommand):
    """
    Check state of songs on filesystem
    """
    option_list = BaseCommand.option_list + (
        make_option('-t', '--type', dest='import_type',
            default='radios', help="import type: radios|static"),
        make_option('-i', '--input', dest='import_directory',
            default='.', help="import directory"),
    )
    help = "Import data from radioways dump files"
    args = ''

    def handle(self, *app_labels, **options):
        import_type = options.get('import_type')
        import_directory =  options.get('import_directory')

        if import_type == 'static':
            import_continent(os.path.join(import_directory, 'r_continent.txt'))
            import_country(os.path.join(import_directory, 'YasoundCountry.txt'))
            import_genre(os.path.join(import_directory, 'YasoundGenre.txt'))

            logger.info('done')
        elif import_type == 'radios':
            import_radio(os.path.join(import_directory, 'YasoundRadio.txt'))
            import_radio_genre(os.path.join(import_directory, 'YasoundRadioGenre.txt'))
            logger.info('done')
        else:
            logger.error('unknown import type')


