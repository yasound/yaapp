from django.core.management.base import BaseCommand
from optparse import make_option
from account.models import UserProfile, UserAdditionalInfosManager
from yacore import geoip

import logging
logger = logging.getLogger("yaapp.account")


class Command(BaseCommand):
    """
    Extract covers
    """
    option_list = BaseCommand.option_list + (
        make_option('-u', '--url', dest='url',
                    default=None, help="url: url to open in message"),
    )
    help = "get geoip from account and save it int additional info"
    args = ''

    def handle(self, *app_labels, **options):
        profiles = UserProfile.objects.filter(latitude__isnull=False)
        ua = UserAdditionalInfosManager()
        logger.info('processing %d accounts' % (profiles.count()))
        for profile in profiles:
            lat = profile.latitude
            lon = profile.longitude

            place = geoip.extendedFindNearby(lat, lon)
            if hasattr(place, 'geoname'):
                geo_info = {}
                for item in place.geoname:
                    geo_info[item.fcode] = item.name

                ua.add_information(profile.user.id, 'geo_info', geo_info)

        logger.info('done')
