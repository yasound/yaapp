# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from optparse import make_option
from yarecommendation.models import ClassifiedRadiosManager,\
    RadiosClusterManager
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
        cm = ClassifiedRadiosManager()
        rc = RadiosClusterManager()
        rc.drop()
        logger.info("creating cluster")
        start = time()
        radios = cm.collection.find()
        for radio in radios:
            rc = RadiosClusterManager()
            rc.add_radio(radio)
        elapsed = time() - start
        logger.info('done in %s secondes', str(elapsed))
        
        
