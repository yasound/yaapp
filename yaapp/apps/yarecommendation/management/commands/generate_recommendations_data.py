# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from optparse import make_option
from yarecommendation.models import ClassifiedRadiosManager
import logging
from time import time

logger = logging.getLogger("yaapp.yarecommendation")


class Command(BaseCommand):
    """
    Check state of songs on filesystem
    """
    option_list = BaseCommand.option_list + (
    )
    help = "Build radio recommendation data"
    args = ''

    def handle(self, *app_labels, **options):
        logger.info("processing radios")
        cm = ClassifiedRadiosManager()
        start = time()
        cm.populate()
        elapsed = time() - start
        logger.info('done in %s secondes', str(elapsed))
        logger.info("calculating similarities")
        start = time()
        cm.calculate_similar_radios()
        elapsed = time() - start
        logger.info('done in %s secondes', str(elapsed))
        logger.info("processing done")
        logger.info("done")
        
