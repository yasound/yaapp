from django.conf import settings
from yabase import settings as yabase_settings, signals as yabase_signals
from yagraph.task import async_post_message, async_listen, async_like_song

def new_wall_event_handler(sender, wall_event, **kwargs):
    user = wall_event.user
    if user is None:
        return
    if user.is_anonymous():
        return
    
    we_type = wall_event.type
    if we_type == yabase_settings.EVENT_MESSAGE:
        async_post_message.delay(user.id, wall_event.radio.uuid, wall_event.text)
    elif we_type == yabase_settings.EVENT_LIKE:
        song_title = unicode(wall_event)
        async_like_song.delay(user.id, wall_event.radio.uuid, song_title)
        
def user_started_listening_handler(sender, radio, user, **kwargs):
    if user is None:
        return
    if user.is_anonymous():
        return
    
    current_song = radio.current_song
    if current_song is None:
        return
    
    song_title = unicode(current_song)
    async_listen.delay(user.id, radio.uuid, song_title)

def install_handlers():
    yabase_signals.new_wall_event.connect(new_wall_event_handler)
    yabase_signals.user_started_listening.connect(user_started_listening_handler)
if settings.FACEBOOK_OPEN_GRAPH_ENABLED:
    install_handlers()    