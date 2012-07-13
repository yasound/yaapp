# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from optparse import make_option
from yarecommendation.models import ClassifiedRadiosManager, MapArtistManager,\
    RadiosKMeansManager
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
        make_option('-c', '--cluster', dest='use_cluster', action='store_true',
            default=False, help="use cluster"),
    )
    help = "Build radio recommendation data"
    args = ''

    def handle(self, *app_labels, **options):
        start = time()
        radio_id = int(options.get('radio_id', 0))
        use_cluster = options.get('use_cluster', False)
        logger.info("getting recommendation")
        cm = ClassifiedRadiosManager()
        
        doc = cm.radio_doc(radio_id)
        if doc is None:
            logger.info('radio not found, exiting')
            return
        
        artists = doc.get('artists')
        
        result = []
        if not use_cluster:
            ma = MapArtistManager()
            artists_names = [ma.artist_name(code) for code in artists]
            reco = cm.find_similar_radios(artists_names)
            for rec in reco:
                if rec[1] == radio_id:
                    continue
                result.append(rec)
        else:
            rk = RadiosKMeansManager()
            doc = cm.collection.find_one({'db_id': radio_id})
            result = rk.find_cluster(doc.get('classification'))
        logger.info(result)
        elapsed = time() - start
        logger.info('done in %s secondes', str(elapsed))             