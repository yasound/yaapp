from django.conf.urls.defaults import *

urlpatterns = patterns('yabackoffice.views',
    url(r'^$', 'index', name='yabackoffice_index'),
    url(r'^radio/(?P<radio_id>\d+)/unmatched/$', 'radio_unmatched_song'),
)