import django.dispatch

new_notification  = django.dispatch.Signal(providing_args=['notification'])
unread_changed = django.dispatch.Signal(providing_args=['dest_user_id', 'count'])