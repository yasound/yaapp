# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from optparse import make_option
from account.models import UserProfile, UserAdditionalInfosManager
from yacore import geoip

import logging
logger = logging.getLogger("yaapp.account")


FRANCOPHONE_COUNTRIES = (
    u'france',
    u'réunion',
    u'martinique',
    u'guadeloupe',
    u'algeria',
    u'tunisia',
    u'morocco',
    u'switzerland',
    u'quebec',
    u'belgium',
)

class Command(BaseCommand):
    """
    Extract covers
    """
    option_list = BaseCommand.option_list + (
        make_option('-u', '--url', dest='url',
                    default=None, help="url: url to open in message"),
    )
    help = "update account language settings based on geoip informations"
    args = ''

    def handle(self, *app_labels, **options):
        profiles = UserProfile.objects.select_related().filter(latitude__isnull=False)
        ua = UserAdditionalInfosManager()
        logger.info('processing %d accounts' % (profiles.count()))
        for profile in profiles:
            additional_info = ua.information(profile.user.id)
            if additional_info and additional_info.get('geo_info') is not None:
                country = additional_info.get('geo_info').get('PCLI', '').lower()
                if country == '':
                    country = additional_info.get('geo_info').get('PCLD', '').lower()
                if country == u'canada':
                    country = additional_info.get('geo_info').get('ADM1', '').lower()
                print country
                if country not in FRANCOPHONE_COUNTRIES and country != '':
                    profile.language = 'en'
                    profile.save()
        logger.info('done')
