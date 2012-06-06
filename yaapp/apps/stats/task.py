from celery.task import task
from yabase.models import Radio
import logging
logger = logging.getLogger("yaapp.stats")

@task
def radio_listening_stats_task():
    logger.info('radio_listening_stats_task started')
    radios = Radio.objects.filter(ready=True)
    for radio in radios:
        if radio.id == 165:
            logger.info('radio 165 updated')
        radio.create_listening_stat()
    logger.info('radio_listening_stats_task finished')
