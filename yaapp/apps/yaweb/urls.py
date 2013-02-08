from django.conf.urls.defaults import *

urlpatterns = patterns('yaweb.views',
    # url(r'^about/$', 'about', {'template_name': 'yaweb/about.html'}, name='about'),
    # url(r'^jobs/$', 'jobs', {'template_name': 'yaweb/jobs.html'}, name='jobs'),
    # url(r'^press/$', 'press', {'template_name': 'yaweb/press.html'}, name='press'),
    # url(r'^contact/$', 'contact', {'template_name': 'yaweb/contact.html'}, name='contact'),
    url(r'^elecsounds/$', 'elecsounds', {'template_name': 'yaweb/elecsounds.html'}, name='elecsounds'),
    url(r'^elecsounds/terms$', 'elecsounds_terms', {'template_name': 'yaweb/elecsounds_terms.html'}, name='elecsounds_terms'),
    url(r'^elecsounds/winner', 'elecsounds_winner', {'template_name': 'yaweb/elecsounds_winner.html'}, name='elecsounds_winner'),
    url(r'^station/$', 'contest_station', {'template_name': 'yaweb/contest_station.html'}, name='contest_station'),
    url(r'^concours/valentine_2013/$', 'valentine_2013', name='valentine_2013'),
    url(r'^concours/valentine_2013/iphone/$', 'valentine_2013_iphone', name='valentine_2013_iphone'),
    url(r'^premium_win/$', 'premium_win', {'template_name': 'yaweb/premium_win.html'}, name='premium_win'),
    url(r'^station/iphone/$', 'contest_station_iphone', {'template_name': 'yaweb/contest_station_iphone.html'}, name='contest_station_iphone'),
    url(r'^station/terms/$', 'contest_station_terms', {'template_name': 'yaweb/contest_station_terms.html'}, name='contest_station_terms'),

    url(r'^betatest/$', 'betatest', name='betatest_survey'),
    url(r'^betatest/thank-you$', 'betatest_thankyou', name='betatest_thankyou'),


    url(r'^download/(?P<filename>.*)$', 'download', name='download'),

    url(r'^fr/(?P<url>.*)', 'redirect'),
    url(r'^en/(?P<url>.*)', 'redirect')
)