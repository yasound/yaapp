from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.urlresolvers import reverse
from optparse import make_option
import logging
from account.models import UserProfile

logger = logging.getLogger("yaapp.account")

class Command(BaseCommand):
    """
    Update friends count
    """
    option_list = BaseCommand.option_list + (
    )
    help = "Update friends count"
    args = ''

    def handle(self, *app_labels, **options):
        profiles = UserProfile.objects.all()
        logger.info("computing %d users" % (profiles.count()))
        for profile in profiles:
            profile.update_friends_count()
        logger.info("done")


