# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from optparse import make_option
from yabase.models import Radio, WallEvent
from yabase import settings as yabase_settings
from yawall.models import WallManager
import logging

logger = logging.getLogger("yaapp.yawall")


class Command(BaseCommand):
    """
    Convert all messages to new messages
    """
    option_list = BaseCommand.option_list + (
    )
    help = "Convert old wall events to new system"
    args = ''

    def handle(self, *app_labels, **options):
        logger.info("starting import")
        wm = WallManager()

        radios = Radio.objects.filter(ready=True, deleted=False)
        for radio in radios:
            wall_events = WallEvent.objects.filter(radio=radio)
            imported_count = 0
            count = wall_events.count()
            if count == 0:
                continue
            logger.info('analyzing radio %s (%s): %d messages' % (radio.id, radio.uuid, count))
            for wall_event in wall_events:
                if wall_event.type == yabase_settings.EVENT_MESSAGE:
                    existing_event = wm.find_existing_event(event_type=WallManager.EVENT_MESSAGE,
                                                            radio_uuid=radio.uuid,
                                                            message=wall_event.text,
                                                            date=wall_event.start_date,
                                                            username=wall_event.user.username)

                    if not existing_event:
                        imported_count += 1
                        wm.import_old_event(wall_event)
                elif wall_event.type == yabase_settings.EVENT_LIKE:
                    existing_event = wm.find_existing_event(event_type=WallManager.EVENT_LIKE,
                                                            radio_uuid=radio.uuid,
                                                            date=wall_event.start_date,
                                                            username=wall_event.user.username,
                                                            song=wall_event.song)

                    if not existing_event:
                        imported_count += 1
                        wm.import_old_event(wall_event)
            logger.info('analyzed radio %s (%s): imported %d messages' % (radio.id, radio.uuid, imported_count))

        logger.info("done")
