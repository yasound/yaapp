# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from optparse import make_option
from time import time
from yarecommendation.models import ClassifiedRadiosManager, RadiosKMeansManager
import logging

logger = logging.getLogger("yaapp.yarecommendation")


class Command(BaseCommand):
    """
    Check state of songs on filesystem
    """
    option_list = BaseCommand.option_list + (
    )
    help = "Build radio recommendation data (kmean)"
    args = ''

    def handle(self, *app_labels, **options):
        logger.info("creating cache")
        start = time()
        rk = RadiosKMeansManager()
        rk.save_cache()
        elapsed = time() - start
        logger.info('cache saved in %s seconds', str(elapsed))
        
        
