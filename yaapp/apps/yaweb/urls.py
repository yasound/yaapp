from django.conf.urls.defaults import *

urlpatterns = patterns('yaweb.views',
    url(r'^about/$', 'about', name='about'),
    url(r'^jobs/$', 'jobs', name='jobs'),
    url(r'^press/$', 'press', name='press'),
    url(r'^contact/$', 'contact', name='contact'),
    url(r'^download/(?P<filename>.*)$', 'download', name='download'),
    url(r'^elecsounds/$', 'elecsounds', name='elecsounds'),
    url(r'^elecsounds/terms$', 'elecsounds_terms', name='elecsounds_terms'),
    
    url(r'^fr/(?P<url>.*)', 'redirect'),
    url(r'^en/(?P<url>.*)', 'redirect')
)