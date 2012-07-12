# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from optparse import make_option
from time import time
from yarecommendation.models import ClassifiedRadiosManager, \
    RadiosClusterManager, RadiosKMeansManager
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
        logger.info("creating cluster")
        start = time()
        rk = RadiosKMeansManager()
        rk.build_cluster()
        elapsed = time() - start
        logger.info('done in %s secondes', str(elapsed))
        
        
