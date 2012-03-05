from django.conf.urls.defaults import *

urlpatterns = patterns('yabackoffice.views',
    url(r'^$', 'index', name='yabackoffice_index'),
    url(r'^radios/(?P<radio_id>\d+)/unmatched/$', 'radio_unmatched_song'),
    url(r'^radios/(?P<radio_id>\d+)/songs/$', 'radio_songs'),
    url(r'^radios/(?P<radio_id>\d+)/remove_songs/$', 'radio_remove_songs'),
    url(r'^radios$', 'radios'),
    url(r'^radios/(?P<radio_id>\d+)$', 'radios'),
    url(r'^invitations/$', 'invitations'),
)