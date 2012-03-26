from django.conf.urls.defaults import *

urlpatterns = patterns('yaweb.views',
    url(r'^about/$', 'about', name='about'),
    url(r'^jobs/$', 'jobs', name='jobs'),
    url(r'^press/$', 'press', name='press'),
    url(r'^contact/$', 'contact', name='contact'),
)