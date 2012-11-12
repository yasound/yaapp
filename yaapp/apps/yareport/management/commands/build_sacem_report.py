from django.core.management.base import BaseCommand
from optparse import make_option
import logging
logger = logging.getLogger("yaapp.yareport")
from yareport.models import sacem_report
from datetime import datetime

class Command(BaseCommand):
    """
    Update action states
    """
    option_list = BaseCommand.option_list + (
        make_option('-s', '--startdate', dest='start_date', action='store',
            default=None, help="report start date (01/31/2012)"),
        make_option('-e', '--enddate', dest='end_date', action='store',
            default=None, help="report end date (01/31/2012)"),
        make_option('-o', '--outdir', dest='out_dir', action='store',
            default='', help="output directory"),
    )
    help = "Build song report for SACEM"
    args = ''

    def handle(self, *app_labels, **options):
        start_date = options.get('start_date', None)
        end_date = options.get('end_date', None)
        out_dir = options.get('out_dir', '')

        if start_date:
            start_date = datetime.strptime(start_date, '%m/%d/%Y')
        if end_date:
            end_date = datetime.strptime(end_date, '%m/%d/%Y')

        print 'start date: %s' % start_date
        print 'end date: %s' % end_date
        sacem_report(out_dir, start_date=start_date, end_date=end_date)


