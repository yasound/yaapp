import django.dispatch

new_device_registered = django.dispatch.Signal(providing_args=['user', 'uuid', 'ios_token'])
facebook_account_added = django.dispatch.Signal(providing_args=['user'])
facebook_account_removed = django.dispatch.Signal(providing_args=['user'])
twitter_account_added = django.dispatch.Signal(providing_args=['user'])
twitter_account_removed = django.dispatch.Signal(providing_args=['user'])
yasound_account_added = django.dispatch.Signal(providing_args=['user'])
yasound_account_removed = django.dispatch.Signal(providing_args=['user'])
