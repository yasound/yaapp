from django.db import models
from yabase import settings as yabase_settings, signals as yabase_signals
from yagraph.task import async_post_message

def new_wall_event_handler(sender, wall_event, **kwargs):
    user = wall_event.user
    if user is None:
        return
    if user.is_anonymous():
        return
    
    we_type = wall_event.type
    if we_type == yabase_settings.EVENT_MESSAGE:
        async_post_message.delay(user.id, wall_event.radio.uuid, wall_event.text)

def install_handlers():
    yabase_signals.new_wall_event.connect(new_wall_event_handler)
install_handlers()    