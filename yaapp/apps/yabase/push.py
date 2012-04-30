from django.conf import settings
from redis import Redis
import signals as yabase_signals
import logging
import json

logger = logging.getLogger("yaapp.yabase")

REDIS_HOST = getattr(settings, 'REDIS_HOST', 'localhost')

def push_wall_event(wall_event, **kwargs):
    red = Redis(REDIS_HOST)
    channel = 'radio.%s' % (wall_event.radio.id)
    logger.info("publishing message to %s" % (channel)) 
    
    from api import RadioWallEventResource
    we = RadioWallEventResource() 
    we_bundle = we.build_bundle(obj=wall_event, request=None)
    serialized_we = we.serialize(None, we.full_dehydrate(we_bundle), 'application/json'),
    data = {
        'event_type': 'wall_event',
        'data':  json.loads(serialized_we[0])
    }
    json_data = json.JSONEncoder(ensure_ascii=False).encode(data)
    red.publish(channel, json_data)

def push_current_song(radio, song_json, **kwargs):
    red = Redis(REDIS_HOST)
    channel = 'radio.%s' % (radio.id)
    data = {
        'event_type': 'song',
        'data':  json.loads(song_json)
    }
    
    json_data = json.JSONEncoder(ensure_ascii=False).encode(data)
    red.publish(channel, json_data)
    

def install_handlers():
    yabase_signals.new_wall_event.connect(push_wall_event)
    yabase_signals.new_current_song.connect(push_current_song)
