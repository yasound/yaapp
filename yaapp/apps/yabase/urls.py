from django.conf.urls.defaults import *
from yabase.views import WebAppView

urlpatterns = patterns('yabase.views',

    # web application
    url(r'^$', WebAppView.as_view(), {'page': 'home'}, name='webapp_default'),
    url(r'^radio/(?P<radio_uuid>\w+)/$', WebAppView.as_view(),  {'page': 'radio'}, name='webapp_default_radio'),
    url(r'^search/(?P<query>\S+)/$',  WebAppView.as_view(),  {'page': 'search'}, name='webapp_default_search'),
    url(r'^radios/$', WebAppView.as_view(), {'page': 'radios'}, name='webapp_default_radios'),
    url(r'^radios/new/$', WebAppView.as_view(), {'page': 'new_radio'}, name='webapp_default_new_radio'),
    url(r'^favorites/$', WebAppView.as_view(), {'page': 'favorites'}, name='webapp_default_favorites'),
    url(r'^top/$', WebAppView.as_view(), {'page': 'top'}, name='webapp_default_top'),
    url(r'^friends/$', WebAppView.as_view(), {'page': 'friends'}, name='webapp_default_friends'),
    url(r'^settings/$', WebAppView.as_view(), {'page': 'settings'}, name='webapp_default_settings'),
    url(r'^notifications/$', WebAppView.as_view(), {'page': 'notifications'}, name='webapp_default_notifications'),
    url(r'^programming/$', WebAppView.as_view(), {'page': 'programming'}, name='webapp_default_programming'),
    url(r'^radio/(?P<radio_uuid>\w+)/programming/$', WebAppView.as_view(),  {'page': 'programming'}, name='webapp_default_programming'),
    url(r'^radio/(?P<radio_uuid>\w+)/edit/$', WebAppView.as_view(),  {'page': 'edit_radio'}, name='webapp_default_edit_radio'),
    url(r'^radio/(?P<radio_uuid>\w+)/listeners/$', WebAppView.as_view(),  {'page': 'listeners'}, name='webapp_default_listeners'),
    url(r'^legal/$', WebAppView.as_view(), {'page': 'legal'}, name='webapp_default_legal'),
    url(r'^contact/$', WebAppView.as_view(), {'page': 'contact'}, name='webapp_default_contact'),
    url(r'^signup/$', WebAppView.as_view(), {'page': 'signup'}, name='webapp_default_signup'),
    url(r'^login/$', WebAppView.as_view(), {'page': 'login'}, name='webapp_default_login'),
    url(r'^users/$', WebAppView.as_view(), {'page': 'users'}, name='webapp_default_users'),
    url(r'^gifts/$', WebAppView.as_view(), {'page': 'gifts'}, name='webapp_default_gifts'),
    url(r'^profile/(?P<user_id>\S+)/$', WebAppView.as_view(), {'page': 'profile'}, name='webapp_default_profile'),

    url(r'^tpl/(?P<template_name>\S+)/$', 'load_template'),


    url(r'^(?P<app_name>\w+)/$', WebAppView.as_view(), {'page': 'home'}, name='webapp'),
    url(r'^(?P<app_name>\w+)/radio/(?P<radio_uuid>\w+)/$', WebAppView.as_view(),  {'page': 'radio'}, name='webapp_radio'),
    url(r'^(?P<app_name>\w+)/search/(?P<query>\S+)/$',  WebAppView.as_view(),  {'page': 'search'}, name='webapp_search'),
    url(r'^(?P<app_name>\w+)/radios/$', WebAppView.as_view(), {'page': 'radios'}, name='webapp_radios'),
    url(r'^(?P<app_name>\w+)/radios/new/$', WebAppView.as_view(), {'page': 'new_radio'}, name='webapp_new_radio'),
    url(r'^(?P<app_name>\w+)/favorites/$', WebAppView.as_view(), {'page': 'favorites'}, name='webapp_favorites'),
    url(r'^(?P<app_name>\w+)/top/$', WebAppView.as_view(), {'page': 'top'}, name='webapp_top'),
    url(r'^(?P<app_name>\w+)/friends/$', WebAppView.as_view(), {'page': 'friends'}, name='webapp_friends'),
    url(r'^(?P<app_name>\w+)/settings/$', WebAppView.as_view(), {'page': 'settings'}, name='webapp_settings'),
    url(r'^(?P<app_name>\w+)/notifications/$', WebAppView.as_view(), {'page': 'notifications'}, name='webapp_notifications'),
    url(r'^(?P<app_name>\w+)/programming/$', WebAppView.as_view(), {'page': 'programming'}, name='webapp_programming'),
    url(r'^(?P<app_name>\w+)/radio/(?P<radio_uuid>\w+)/programming/$', WebAppView.as_view(),  {'page': 'programming'}, name='webapp_programming'),
    url(r'^(?P<app_name>\w+)/radio/(?P<radio_uuid>\w+)/edit/$', WebAppView.as_view(),  {'page': 'edit_radio'}, name='webapp_edit_radio'),
    url(r'^(?P<app_name>\w+)/radio/(?P<radio_uuid>\w+)/listeners/$', WebAppView.as_view(),  {'page': 'listeners'}, name='webapp_listeners'),
    url(r'^(?P<app_name>\w+)/legal/$', WebAppView.as_view(), {'page': 'legal'}, name='webapp_legal'),
    url(r'^(?P<app_name>\w+)/contact/$', WebAppView.as_view(), {'page': 'contact'}, name='webapp_contact'),
    url(r'^(?P<app_name>\w+)/signup/$', WebAppView.as_view(), {'page': 'signup'}, name='webapp_signup'),
    url(r'^(?P<app_name>\w+)/login/$', WebAppView.as_view(), {'page': 'login'}, name='webapp_login'),
    url(r'^(?P<app_name>\w+)/users/$', WebAppView.as_view(), {'page': 'users'}, name='webapp_users'),
    url(r'^(?P<app_name>\w+)/gifts/$', WebAppView.as_view(), {'page': 'gifts'}, name='webapp_gifts'),
    url(r'^(?P<app_name>\w+)/profile/(?P<user_id>\S+)/$', WebAppView.as_view(), {'page': 'profile'}, name='webapp_profile'),

    url(r'^(?P<app_name>\w+)/tpl/(?P<template_name>\S+)/$', 'load_template'),

    url(r'^(?P<app_name>\w+)/logout/$', 'logout'),
)
