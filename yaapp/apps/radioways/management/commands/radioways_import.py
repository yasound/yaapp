# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from optparse import make_option

import logging
logger = logging.getLogger("yaapp.radioways")
import os
from radioways.import_utils import *


class Command(BaseCommand):
    """
    Check state of songs on filesystem
    """
    option_list = BaseCommand.option_list + (
        make_option('-t', '--type', dest='import_type',
                    default='', help="import type: radios|static|logos"),
        make_option('-i', '--input', dest='import_directory',
            default='.', help="import directory"),
        make_option('-a', '--activate', dest='activate', action='store_true',
            default=0, help="activate radioways radios (create yasound radios)"),
    )
    help = "Import data from radioways dump files"
    args = ''

    def handle(self, *app_labels, **options):
        activate = options.get('activate', False)
        import_type = options.get('import_type')
        import_directory = options.get('import_directory')

        logger.info('------------------------------------')
        logger.info('activate: %s', activate)
        logger.info('import type: %s', import_type)
        logger.info('import directory: %s', import_directory)
        logger.info('------------------------------------')

        if import_type == 'static':
            logger.info('importing static data')
            import_continent(os.path.join(import_directory, 'r_continent.txt'))
            import_country(os.path.join(import_directory, 'YasoundCountry.txt'))
            import_genre(os.path.join(import_directory, 'YasoundGenre.txt'))
        elif import_type == 'radios':
            logger.info('importing radio')
            import_radio(os.path.join(import_directory, 'YasoundRadio.txt'))
            import_radio_genre(os.path.join(import_directory, 'YasoundRadioGenre.txt'))
        elif import_type == 'logos':
            logger.info('importing logos')
            import_logos(os.path.join(import_directory, 'logos'))

        if activate:
            logger.info('activating radios (links with yasound radios)')
            link_to_yasound()
        logger.info('done')
