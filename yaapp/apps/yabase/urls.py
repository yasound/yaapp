from django.conf.urls.defaults import *
from yabase.views import WebAppView

urlpatterns = patterns('yabase.views',
    
    # web application                   
    
    url(r'^app/$', WebAppView.as_view(), {'page': 'home'}, name='webapp'),
    url(r'^app/radio/(?P<radio_uuid>\S+)/$', WebAppView.as_view(),  {'page': 'radio'}, name='webapp_radio'),
    url(r'^app/search/(?P<query>\S+)/$',  WebAppView.as_view(),  {'page': 'search'}, name='webapp_search'),
    url(r'^app/favorites/$', WebAppView.as_view(), {'page': 'favorites'}, name='webapp_favorites'),
    url(r'^app/top/$', WebAppView.as_view(), {'page': 'top'}, name='webapp_top'),
    url(r'^app/friends/$', WebAppView.as_view(), {'page': 'friends'}, name='webapp_friends'),
    url(r'^app/settings/$', WebAppView.as_view(), {'page': 'settings'}, name='webapp_settings'),
    url(r'^app/notifications/$', WebAppView.as_view(), {'page': 'notifications'}, name='webapp_notifications'),
    url(r'^app/programming/$', WebAppView.as_view(), {'page': 'programming'}, name='webapp_programming'),
    url(r'^app/legal/$', WebAppView.as_view(), {'page': 'legal'}, name='webapp_legal'),
    url(r'^app/contact/$', WebAppView.as_view(), {'page': 'contact'}, name='webapp_contact'),
    url(r'^app/users/$', WebAppView.as_view(), {'page': 'users'}, name='webapp_users'),
    url(r'^app/profile/(?P<user_id>\S+)/$', WebAppView.as_view(), {'page': 'profile'}, name='webapp_profile'),

    url(r'^app/tpl/(?P<template_name>\S+)/$', 'load_template'),
)