from django.core.management.base import BaseCommand
from optparse import make_option
from yamenu.models import MenusManager
import logging
logger = logging.getLogger("yaapp.yamenu")

class Command(BaseCommand):
    """
    Update action states
    """
    option_list = BaseCommand.option_list + (
        make_option('-c', '--clear', dest='clear', action='store_true',
            default=False, help="clear : remove all menu descriptions before re-installing defaults"),
    )
    help = "Install default menu descriptions"
    args = ''

    def handle(self, *app_labels, **options):
        clear = options.get('clear',False)
        mm = MenusManager()
        if clear:
            mm.clear()
        mm.install_defaults()
