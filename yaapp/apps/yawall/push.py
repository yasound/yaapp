from celery.task import task
from django.conf import settings
from django.db.models import signals
from redis import Redis
import signals as yabase_signals
import logging
from django.utils import simplejson
import signals as yawall_signals
from yacore.api import MongoAwareEncoder

logger = logging.getLogger("yaapp.yawall")


@task(ignore_result=True)
def async_redis_publish(channel, json_data):
    red = Redis(host=settings.PUSH_REDIS_HOST, db=settings.PUSH_REDIS_DB)
    logger.info("-->publishing message to %s" % (channel))
    red.publish(channel, json_data)


def push_wall_event(event, **kwargs):
    channel = 'radio.%s' % (event.get('radio_id'))

    logger.info("publishing message to %s" % (channel))

    data = {
        'event_type': 'wall_event_v2_updated',
        'data': simplejson.dumps(event, cls=MongoAwareEncoder)
    }
    try:
        json_data = simplejson.dumps(data, cls=MongoAwareEncoder)
        async_redis_publish.delay(channel, json_data)
    except:
        pass


def push_wall_event_deleted(sender, event, **kwargs):
    channel = 'radio.%s' % (event.get('radio_id'))
    logger.info("publishing message to %s" % (channel))

    data = {
        'event_type': 'wall_event_v2_deleted',
        'data': simplejson.dumps(event, cls=MongoAwareEncoder)
    }
    try:
        json_data = simplejson.dumps(data, cls=MongoAwareEncoder)
        async_redis_publish.delay(channel, json_data)
    except:
        pass


def install_handlers():
    yawall_signals.wall_event_updated.connect(push_wall_event)
    yawall_signals.wall_event_deleted.connect(push_wall_event_deleted)
