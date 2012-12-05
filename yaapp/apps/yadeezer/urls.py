from django.conf.urls.defaults import *

urlpatterns = patterns('yadeezer.views',
    url(r'^deezer/channel_url/$', 'channel_url', name='deezer_channel'),
    url(r'^deezer/communication/(?P<username>\S+)/$', 'deezer_communication', name='deezer_communication'),

    url(r'^api/v1/deezer/import_track/(?P<radio_uuid>\S+)/$', 'import_track'),
)
