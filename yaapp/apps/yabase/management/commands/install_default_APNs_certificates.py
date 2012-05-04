from django.core.management.base import BaseCommand
from optparse import make_option
from yabase.models import ApnsCertificate
import logging
logger = logging.getLogger("yaapp.yabase")

class Command(BaseCommand):
    """
    Update action states
    """
    help = "Install default APNs certificate paths in db"
    args = ''

    def handle(self, *app_labels, **options):
        ApnsCertificate.objects.install_defaults()
