from django.conf.urls.defaults import *

urlpatterns = patterns('yaweb.views',
    url(r'^about/$', 'about', name='about'),
    url(r'^jobs/$', 'jobs', name='jobs'),
    url(r'^press/$', 'press', name='press'),
    url(r'^contact/$', 'contact', name='contact'),
    url(r'^download/(?P<filename>.*)$', 'download', name='download'),
    
    url(r'^fr/(?P<url>.*)', 'redirect'),
    url(r'^en/(?P<url>.*)', 'redirect')
)