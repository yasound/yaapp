"""
Signals declaration for yabase
"""
import django.dispatch

buy_link = django.dispatch.Signal(providing_args=['radio', 'user', 'song_instance'])
user_watched_tutorial = django.dispatch.Signal(providing_args=['user'])
user_started_listening = django.dispatch.Signal(providing_args=['radio', 'user'])
user_stopped_listening = django.dispatch.Signal(providing_args=['radio', 'user', 'duration'])
new_wall_event = django.dispatch.Signal(providing_args=['wall_event'])
dislike_radio = django.dispatch.Signal(providing_args=['radio', 'user'])
like_radio = django.dispatch.Signal(providing_args=['radio', 'user'])
neutral_like_radio = django.dispatch.Signal(providing_args=['radio', 'user'])
favorite_radio = django.dispatch.Signal(providing_args=['radio', 'user'])
not_favorite_radio = django.dispatch.Signal(providing_args=['radio', 'user'])
new_current_song = django.dispatch.Signal(providing_args=['radio', 'song_json', 'song'])
access_my_radios = django.dispatch.Signal(providing_args=['user'])

radio_metadata_updated = django.dispatch.Signal(providing_args=['radio'])
radio_shared = django.dispatch.Signal(providing_args=['radio', 'user', 'share_type'])
radio_deleted = django.dispatch.Signal(providing_args=['radio', ])
radio_is_ready = django.dispatch.Signal(providing_args=['radio', ])

new_moderator_del_msg_activity = django.dispatch.Signal(providing_args=['user', ])
new_moderator_abuse_msg_activity = django.dispatch.Signal(providing_args=['user', 'wall_event'])

new_animator_activity = django.dispatch.Signal(providing_args=['user', 'radio', 'atype', 'details'])
user_started_listening_song = django.dispatch.Signal(providing_args=['radio', 'user', 'song'])
