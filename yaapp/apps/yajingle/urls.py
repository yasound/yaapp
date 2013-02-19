from django.conf.urls.defaults import *

urlpatterns = patterns('yajingle.views',
    url(r'^radio/(?P<radio_uuid>[\w-]+)/$', 'jingles'),
    url(r'^upload/$', 'upload'),
    url(r'^(?P<id>[\w-]+)/$', 'jingle'),
    url(r'^(?P<id>[\w-]+)/download/$', 'download_jingle'),
)
