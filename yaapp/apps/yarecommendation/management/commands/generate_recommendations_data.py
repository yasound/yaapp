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
    help = "Build radio recommendation data"
    args = ''

    def handle(self, *app_labels, **options):
        logger.info("processing radios")
        cm = ClassifiedRadiosManager()
        cm.drop()
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
        
        logger.info("creating cluster")
        start = time()
        rk = RadiosKMeansManager()
        rk.build_cluster(k=30)
        elapsed = time() - start
        logger.info('done in %s secondes', str(elapsed))

        
