import django.dispatch

user_started_listening  = django.dispatch.Signal(providing_args=['radio', 'user'])
user_stopped_listening  = django.dispatch.Signal(providing_args=['radio', 'user', 'duration'])
new_wall_event          = django.dispatch.Signal(providing_args=['wall_event'])
dislike_radio           = django.dispatch.Signal(providing_args=['radio', 'user'])
like_radio              = django.dispatch.Signal(providing_args=['radio', 'user'])
neutral_like_radio      = django.dispatch.Signal(providing_args=['radio', 'user'])
favorite_radio          = django.dispatch.Signal(providing_args=['radio', 'user'])
not_favorite_radio      = django.dispatch.Signal(providing_args=['radio', 'user'])
new_current_song        = django.dispatch.Signal(providing_args=['radio', 'song_json'])
new_animator_activity   = django.dispatch.Signal(providing_args=['user',])
radio_shared            = django.dispatch.Signal(providing_args=['radio', 'user', 'share_type'])

new_moderator_del_msg_activity = django.dispatch.Signal(providing_args=['user',])
