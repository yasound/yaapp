from django.conf.urls.defaults import *

urlpatterns = patterns('yajingle.views',
    url(r'^radio/(?P<radio_uuid>[\w-]+)/$', 'jingles'),
    url(r'^upload/$', 'upload'),
)
