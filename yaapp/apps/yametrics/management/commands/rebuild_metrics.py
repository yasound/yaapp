from django.core.management.base import BaseCommand
from optparse import make_option
from yametrics.models import UserMetricsManager, TimedMetricsManager
from yametrics import settings as yametrics_settings
import datetime
import logging


logger = logging.getLogger("yaapp.yametrics")


class Command(BaseCommand):
    """
    Regenerate timed metrics
    """
    option_list = BaseCommand.option_list + (
        make_option('-d', '--dry', dest='dry', action='store_true',
                    default=False, help="dry: does nothing"),
    )
    help = "Regenerate timed metrics"
    args = ''

    def _get_or_create(self, slot, activities):
        for doc in self.timed_docs:
            if doc.get('type') == slot:
                return doc
        doc = {
            'type': slot
        }
        for activity in activities:
            doc[activity] = 0
        self.timed_docs.append(doc)
        return doc

    def handle(self, *app_labels, **options):
        dry = options.get('dry', False)
        logger.info('rebuilding metrics..')
        uh = UserMetricsManager()
        tm = TimedMetricsManager()
        activities = yametrics_settings.ACTIVITIES

        now = datetime.datetime.now()

        self.timed_docs = []

        for doc in uh.all():
            for activity in activities:
                key_last_date = 'last_%s_date' % (activity)
                key_last_slot = 'last_%s_slot' % (activity)
                last_activity_date = doc[key_last_date] if key_last_date in doc else None
                last_activity_slot = doc[key_last_slot] if key_last_slot in doc else None

                if last_activity_slot is None or last_activity_date is None:
                    continue

                value = doc.get(activity)
                if value is None:
                    value = 0

                days = 0
                if last_activity_date:
                    diff = (now - last_activity_date)
                    days = diff.days
                slot = tm.slot(days)

                timed_doc = self._get_or_create(slot, activities)
                current_value = timed_doc.get(activity)
                if current_value is None:
                    current_value = 0
                timed_doc[activity] = current_value + value

        if not dry:
            logger.info('saving data..')
            for doc in self.timed_docs:
                tm.collection.update({'type': doc.get('type')}, {'$set': doc}, upsert=True, safe=True)
            logger.info('..done')

        logger.info(self.timed_docs)
        logger.info("done")
