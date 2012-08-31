from django.conf.urls.defaults import *

urlpatterns = patterns('yadeezer.views',
    url(r'^channel_url/$', 'channel_url', name='deezer_channel'),
    url(r'^import_track/(?P<radio_uuid>\S+)/$', 'import_track'),
)
