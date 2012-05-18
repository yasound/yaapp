import django.dispatch

new_device_registered  = django.dispatch.Signal(providing_args=['user', 'uuid', 'ios_token'])
