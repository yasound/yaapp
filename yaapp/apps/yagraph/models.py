from django.conf import settings
from yabase import settings as yabase_settings, signals as yabase_signals
from yagraph.task import async_post_message, async_listen, async_like_song, \
    async_animator_activity

def new_wall_event_handler(sender, wall_event, **kwargs):
    user = wall_event.user
    if user is None:
        return
    if user.is_anonymous():
        return

    we_type = wall_event.type
    if we_type == yabase_settings.EVENT_MESSAGE:
        if not user.get_profile().notifications_preferences.fb_share_post_message:
            return
        async_post_message.delay(user.id, wall_event.radio.uuid, wall_event.text)
    elif we_type == yabase_settings.EVENT_LIKE:
        if not user.get_profile().notifications_preferences.fb_share_like_song:
            return
        song_title = unicode(wall_event)
        async_like_song.delay(user.id, wall_event.radio.uuid, song_title, wall_event.song.id)

def user_started_listening_song_handler(sender, radio, user, song, **kwargs):
    if user is None:
        return
    if user.is_anonymous():
        return
    if song is None:
        return

    if not user.get_profile().notifications_preferences.fb_share_listen:
        return

    song_title = unicode(song)
    async_listen.delay(user.id, radio.uuid, song_title, song.id)

def new_animator_activity(sender, user, radio, **kwargs):
    """
    Publish animator activity on Facebook
    """
    if user is None or radio is None:
        return
    if user.is_anonymous():
        return

    if not user.get_profile().notifications_preferences.fb_share_animator_activity:
        return

    async_animator_activity.delay(user.id, radio.uuid)

def install_handlers():
    yabase_signals.new_wall_event.connect(new_wall_event_handler)
    yabase_signals.user_started_listening_song.connect(user_started_listening_song_handler)
    yabase_signals.new_animator_activity.connect(new_animator_activity)
if settings.FACEBOOK_OPEN_GRAPH_ENABLED:
    install_handlers()