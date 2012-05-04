from django.core.management.base import BaseCommand
from yamenu.models import MenusManager
import logging
logger = logging.getLogger("yaapp.yamenu")

class Command(BaseCommand):
    """
    Update action states
    """
    help = "Install techtour menu descriptions"
    args = ''

    def handle(self, *app_labels, **options):
        mm = MenusManager()
        mm.install_techtour()
