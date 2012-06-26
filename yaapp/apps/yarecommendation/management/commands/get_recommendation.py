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
        make_option('-r', '--radio', dest='radio_id',
            default=0, help="radio id"),
    )
    help = "Build radio recommendation data"
    args = ''

    def handle(self, *app_labels, **options):
        radio_id = int(options.get('radio_id', 0))
        logger.info("getting recommendation")
        cm = ClassifiedRadiosManager()
        
        doc = cm.radio_doc(radio_id)
        if doc is None:
            logger.info('radio not found, exiting')
            return
        
        artists = doc.get('artists')
        
        reco = cm.find_similar_radios(artists)
        result = []
        for rec in reco:
            if rec[1] == radio_id:
                continue
            result.append(rec)
        logger.info(result)
        logger.info("done")