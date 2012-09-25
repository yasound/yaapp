from django.conf.urls.defaults import *
from yabase.views import WebAppView

urlpatterns = patterns('yabase.views',

    # web application

    url(r'^app/$', WebAppView.as_view(), {'page': 'home'}, name='webapp'),
    url(r'^app/radio/(?P<radio_uuid>\w+)/$', WebAppView.as_view(),  {'page': 'radio'}, name='webapp_radio'),
    url(r'^app/search/(?P<query>\S+)/$',  WebAppView.as_view(),  {'page': 'search'}, name='webapp_search'),
    url(r'^app/radios/$', WebAppView.as_view(), {'page': 'radios'}, name='webapp_radios'),
    url(r'^app/radios/new/$', WebAppView.as_view(), {'page': 'new_radio'}, name='webapp_new_radio'),
    url(r'^app/favorites/$', WebAppView.as_view(), {'page': 'favorites'}, name='webapp_favorites'),
    url(r'^app/top/$', WebAppView.as_view(), {'page': 'top'}, name='webapp_top'),
    url(r'^app/friends/$', WebAppView.as_view(), {'page': 'friends'}, name='webapp_friends'),
    url(r'^app/settings/$', WebAppView.as_view(), {'page': 'settings'}, name='webapp_settings'),
    url(r'^app/notifications/$', WebAppView.as_view(), {'page': 'notifications'}, name='webapp_notifications'),
    url(r'^app/programming/$', WebAppView.as_view(), {'page': 'programming'}, name='webapp_programming'),
    url(r'^app/radio/(?P<radio_uuid>\w+)/programming/$', WebAppView.as_view(),  {'page': 'programming'}, name='webapp_programming'),
    url(r'^app/radio/(?P<radio_uuid>\w+)/edit/$', WebAppView.as_view(),  {'page': 'edit_radio'}, name='webapp_edit_radio'),
    url(r'^app/radio/(?P<radio_uuid>\w+)/listeners/$', WebAppView.as_view(),  {'page': 'listeners'}, name='webapp_listeners'),
    url(r'^app/legal/$', WebAppView.as_view(), {'page': 'legal'}, name='webapp_legal'),
    url(r'^app/contact/$', WebAppView.as_view(), {'page': 'contact'}, name='webapp_contact'),
    url(r'^app/signup/$', WebAppView.as_view(), {'page': 'signup'}, name='webapp_signup'),
    url(r'^app/login/$', WebAppView.as_view(), {'page': 'login'}, name='webapp_login'),
    url(r'^app/users/$', WebAppView.as_view(), {'page': 'users'}, name='webapp_users'),
    url(r'^app/gifts/$', WebAppView.as_view(), {'page': 'gifts'}, name='webapp_gifts'),
    url(r'^app/profile/(?P<user_id>\S+)/$', WebAppView.as_view(), {'page': 'profile'}, name='webapp_profile'),

    url(r'^app/tpl/(?P<template_name>\S+)/$', 'load_template'),
    url(r'^deezer/tpl/(?P<template_name>\S+)/$', 'load_template', {'root': '/deezer/'}),
)

urlpatterns += (
    url(r'^app/logout/$', 'django.contrib.auth.views.logout', {"next_page": "/app/"}, name="app_logout"),
    url(r'^deezer/logout/$', 'django.contrib.auth.views.logout', {"next_page": "/deezer"}, name="deezer_logout"),
)