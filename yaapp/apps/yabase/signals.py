import django.dispatch

user_stopped_listening  = django.dispatch.Signal(providing_args=['radio', 'user', 'duration'])
new_wall_event          = django.dispatch.Signal(providing_args=['wall_event'])
dislike_radio           = django.dispatch.Signal(providing_args=['radio', 'user'])
like_radio              = django.dispatch.Signal(providing_args=['radio', 'user'])
neutral_like_radio      = django.dispatch.Signal(providing_args=['radio', 'user'])
favorite_radio          = django.dispatch.Signal(providing_args=['radio', 'user'])
not_favorite_radio      = django.dispatch.Signal(providing_args=['radio', 'user'])
