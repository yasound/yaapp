# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from optparse import make_option
from yarecommendation.models import ClassifiedRadiosManager
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
        cm.populate()
        logger.info("calculating similarities")
        cm.calculate_similar_radios()
        logger.info("processing done")
        logger.info("done")
        
