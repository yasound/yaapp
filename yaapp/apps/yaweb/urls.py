from django.conf.urls.defaults import *

urlpatterns = patterns('yaweb.views',
    url(r'^about/$', 'about', {'template_name': 'yaweb/about.html'}, name='about'),
    url(r'^jobs/$', 'jobs', {'template_name': 'yaweb/jobs.html'}, name='jobs'),
    url(r'^press/$', 'press', {'template_name': 'yaweb/press.html'}, name='press'),
    url(r'^contact/$', 'contact', {'template_name': 'yaweb/contact.html'}, name='contact'),
    url(r'^elecsounds/$', 'elecsounds', {'template_name': 'yaweb/elecsounds.html'}, name='elecsounds'),
    url(r'^elecsounds/terms$', 'elecsounds_terms', {'template_name': 'yaweb/elecsounds_terms.html'}, name='elecsounds_terms'),
    #url(r'^elecsounds/winner', 'elecsounds_winner', {'template_name': 'yaweb/elecsounds_winner.html'}, name='elecsounds_winner'),
    
    url(r'^download/(?P<filename>.*)$', 'download', name='download'),

    url(r'^fr/(?P<url>.*)', 'redirect'),
    url(r'^en/(?P<url>.*)', 'redirect')
)