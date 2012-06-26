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
        logger.info("getting recommendation")
        cm = ClassifiedRadiosManager()
        reco = cm.find_similar_radios(['air', 'benjamin biolay', 'the cure'])
        logger.info(reco)
        logger.info("done")