from celery.task import task
from django.conf import settings
from django.db.models import signals
from redis import Redis
import signals as yabase_signals
import logging
import json

logger = logging.getLogger("yaapp.yabase")


@task(ignore_result=True)
def async_redis_publish(channel, json_data):
    red = Redis(host=settings.PUSH_REDIS_HOST, db=settings.PUSH_REDIS_DB)
    logger.info("publishing message to %s" % (channel))
    red.publish(channel, json_data)


def push_wall_event(wall_event, **kwargs):
    if wall_event.radio.nb_current_users == 0:
        return
    channel = 'radio.%s' % (wall_event.radio.id)
    logger.info("publishing message to %s" % (channel))

    from api import RadioWallEventResource
    we = RadioWallEventResource()
    we_bundle = we.build_bundle(obj=wall_event, request=None)
    try:
        serialized_we = we.serialize(None, we.full_dehydrate(we_bundle), 'application/json'),
        data = {
            'event_type': 'wall_event',
            'data': serialized_we[0]
        }
        json_data = json.JSONEncoder(ensure_ascii=False).encode(data)
        async_redis_publish.delay(channel, json_data)
    except:
        pass

def push_wall_event_deleted(sender, instance, created=None, **kwargs):
    wall_event = instance
    if wall_event.radio.nb_current_users == 0:
        return
    channel = 'radio.%s' % (wall_event.radio.id)
    logger.info("publishing message to %s" % (channel))

    from api import RadioWallEventResource
    we = RadioWallEventResource()
    we_bundle = we.build_bundle(obj=wall_event, request=None)

    try:
        serialized_we = we.serialize(None, we.full_dehydrate(we_bundle), 'application/json'),
        data = {
            'event_type': 'wall_event_deleted',
            'data': serialized_we[0]
        }
        json_data = json.JSONEncoder(ensure_ascii=False).encode(data)
        async_redis_publish.delay(channel, json_data)
    except:
        pass

def push_current_song(radio, song_json, song, song_dict, **kwargs):
    if radio.nb_current_users == 0:
        return

    channel = 'radio.%s' % (radio.id)
    data = {
        'event_type': 'song',
        'data': song_json
    }

    json_data = json.JSONEncoder(ensure_ascii=False).encode(data)
    async_redis_publish.delay(channel, json_data)


def install_handlers():
    from models import WallEvent
    signals.pre_delete.connect(push_wall_event_deleted, sender=WallEvent)
    yabase_signals.new_wall_event.connect(push_wall_event)
    yabase_signals.new_current_song.connect(push_current_song)
