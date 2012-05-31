import django.dispatch

new_notification  = django.dispatch.Signal(providing_args=['notification'])
