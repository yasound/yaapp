"""
Signals declaration for yawall
"""
import django.dispatch

wall_event_updated = django.dispatch.Signal(providing_args=['event'])
wall_event_deleted = django.dispatch.Signal(providing_args=['event'])
