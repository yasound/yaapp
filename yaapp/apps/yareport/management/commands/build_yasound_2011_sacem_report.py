from django.core.management.base import BaseCommand
from optparse import make_option
import logging
logger = logging.getLogger("yaapp.yareport")
from yareport.utils import build_yasound_2011_sacem_report_file
from yabase.models import Radio


class Command(BaseCommand):
    """
    Update action states
    """
    option_list = BaseCommand.option_list + (
        make_option('-o', '--outdir', dest='out_dir', action='store',
            default='', help="output directory"),
        make_option('-r', '--radioid', dest='radio_id', action='store',
            default=None, help="id of the radio where to pick songs"),
    )
    help = "Build yasound 2011's song report for SACEM"
    args = ''

    def handle(self, *app_labels, **options):
        out_dir = options.get('out_dir', '')
        radio_id = options.get('radio_id', None)

        radio = None if radio_id is None else Radio.objects.get(id=radio_id)
        build_yasound_2011_sacem_report_file(out_dir, radio=radio)
