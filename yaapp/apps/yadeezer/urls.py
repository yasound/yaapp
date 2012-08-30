from django.conf.urls.defaults import *

urlpatterns = patterns('yadeezer.views',
    url(r'^channel_url/$', 'channel_url', name='deezer_channel'),
)
