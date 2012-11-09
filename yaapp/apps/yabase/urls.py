from django.conf.urls.defaults import *
from yabase.views import WebAppView

urlpatterns = patterns('yabase.views',

    # web application
    url(r'^$', WebAppView.as_view(), {'page': 'home'}, name='webapp_default'),
    url(r'^radio/(?P<radio_uuid>\w+)/$', WebAppView.as_view(),  {'page': 'radio'}, name='webapp_default_radio'),
    url(r'^radio/(?P<radio_uuid>\w+)/(?P<song_id>\d+)/$', WebAppView.as_view(),  {'page': 'song'}, name='webapp_default_radio_song'),
    url(r'^search/(?P<query>\S+)/$',  WebAppView.as_view(),  {'page': 'search'}, name='webapp_default_search'),
    url(r'^radios/$', WebAppView.as_view(), {'page': 'radios'}, name='webapp_default_radios'),
    url(r'^radios/new/$', WebAppView.as_view(), {'page': 'new_radio'}, name='webapp_default_new_radio'),
    url(r'^favorites/$', WebAppView.as_view(), {'page': 'favorites'}, name='webapp_default_favorites'),
    url(r'^favorites/(?P<genre>\w+)/$', WebAppView.as_view(), {'page': 'favorites'}, name='webapp_default_favorites'),
    url(r'^top/$', WebAppView.as_view(), {'page': 'top'}, name='webapp_default_top'),
    url(r'^top/(?P<genre>\w+)/$', WebAppView.as_view(), {'page': 'top'}, name='webapp_default_top'),
    url(r'^friends/$', WebAppView.as_view(), {'page': 'friends'}, name='webapp_default_friends'),
    url(r'^settings/$', WebAppView.as_view(), {'page': 'settings'}, name='webapp_default_settings'),
    url(r'^notifications/$', WebAppView.as_view(), {'page': 'notifications'}, name='webapp_default_notifications'),
    url(r'^programming/$', WebAppView.as_view(), {'page': 'programming'}, name='webapp_default_programming'),
    url(r'^radio/(?P<radio_uuid>\w+)/programming/$', WebAppView.as_view(),  {'page': 'programming'}, name='webapp_default_programming'),
    url(r'^radio/(?P<radio_uuid>\w+)/edit/$', WebAppView.as_view(),  {'page': 'edit_radio'}, name='webapp_default_edit_radio'),
    url(r'^radio/(?P<radio_uuid>\w+)/listeners/$', WebAppView.as_view(),  {'page': 'listeners'}, name='webapp_default_listeners'),
    url(r'^signup/$', WebAppView.as_view(), {'page': 'signup'}, name='webapp_default_signup'),
    url(r'^login/$', WebAppView.as_view(), {'page': 'login'}, name='webapp_default_login'),
    url(r'^users/$', WebAppView.as_view(), {'page': 'users'}, name='webapp_default_users'),
    url(r'^gifts/$', WebAppView.as_view(), {'page': 'gifts'}, name='webapp_default_gifts'),
    url(r'^profile/(?P<user_id>\S+)/$', WebAppView.as_view(), {'page': 'profile'}, name='webapp_default_profile'),

    url(r'^legal/$', WebAppView.as_view(), {'page': 'legal'}, name='webapp_default_legal'),
    url(r'^contact/$', WebAppView.as_view(), {'page': 'contact'}, name='webapp_default_contact'),
    url(r'^about/$', WebAppView.as_view(), {'page': 'about'}, name='webapp_default_about'),
    url(r'^jobs/$', WebAppView.as_view(), {'page': 'jobs'}, name='webapp_default_jobs'),
    url(r'^help/$', WebAppView.as_view(), {'page': 'help'}, name='webapp_default_help'),
    url(r'^press/$', WebAppView.as_view(), {'page': 'press'}, name='webapp_default_press'),
    url(r'^tutorial/$', WebAppView.as_view(), {'page': 'tutorial'}, name='webapp_default_tutorial'),
    url(r'^selection/(?P<genre>\w+)/$', WebAppView.as_view(), {'page': 'home'}, name='webapp_default'),

    url(r'^tpl/(?P<template_name>\S+)/$', 'load_template'),

    url(r'^(?P<app_name>app|deezer)/$', WebAppView.as_view(), {'page': 'home'}, name='webapp'),
    url(r'^(?P<app_name>app|deezer)/radio/(?P<radio_uuid>\w+)/$', WebAppView.as_view(),  {'page': 'radio'}, name='webapp_radio'),
    url(r'^(?P<app_name>app|deezer)/search/(?P<query>\S+)/$',  WebAppView.as_view(),  {'page': 'search'}, name='webapp_search'),
    url(r'^(?P<app_name>app|deezer)/radios/$', WebAppView.as_view(), {'page': 'radios'}, name='webapp_radios'),
    url(r'^(?P<app_name>app|deezer)/radios/new/$', WebAppView.as_view(), {'page': 'new_radio'}, name='webapp_new_radio'),
    url(r'^(?P<app_name>app|deezer)/favorites/$', WebAppView.as_view(), {'page': 'favorites'}, name='webapp_favorites'),
    url(r'^(?P<app_name>app|deezer)/favorites/(?P<genre>\w+)/$', WebAppView.as_view(), {'page': 'favorites'}, name='webapp_favorites'),
    url(r'^(?P<app_name>app|deezer)/top/$', WebAppView.as_view(), {'page': 'top'}, name='webapp_top'),
    url(r'^(?P<app_name>app|deezer)/top/(?P<genre>\w+)/$', WebAppView.as_view(), {'page': 'top'}, name='webapp_top'),
    url(r'^(?P<app_name>app|deezer)/friends/$', WebAppView.as_view(), {'page': 'friends'}, name='webapp_friends'),
    url(r'^(?P<app_name>app|deezer)/settings/$', WebAppView.as_view(), {'page': 'settings'}, name='webapp_settings'),
    url(r'^(?P<app_name>app|deezer)/notifications/$', WebAppView.as_view(), {'page': 'notifications'}, name='webapp_notifications'),
    url(r'^(?P<app_name>app|deezer)/programming/$', WebAppView.as_view(), {'page': 'programming'}, name='webapp_programming'),
    url(r'^(?P<app_name>app|deezer)/radio/(?P<radio_uuid>\w+)/programming/$', WebAppView.as_view(),  {'page': 'programming'}, name='webapp_programming'),
    url(r'^(?P<app_name>app|deezer)/radio/(?P<radio_uuid>\w+)/edit/$', WebAppView.as_view(),  {'page': 'edit_radio'}, name='webapp_edit_radio'),
    url(r'^(?P<app_name>app|deezer)/radio/(?P<radio_uuid>\w+)/listeners/$', WebAppView.as_view(),  {'page': 'listeners'}, name='webapp_listeners'),
    url(r'^(?P<app_name>app|deezer)/signup/$', WebAppView.as_view(), {'page': 'signup'}, name='webapp_signup'),
    url(r'^(?P<app_name>app|deezer)/login/$', WebAppView.as_view(), {'page': 'login'}, name='webapp_login'),
    url(r'^(?P<app_name>app|deezer)/users/$', WebAppView.as_view(), {'page': 'users'}, name='webapp_users'),
    url(r'^(?P<app_name>app|deezer)/gifts/$', WebAppView.as_view(), {'page': 'gifts'}, name='webapp_gifts'),
    url(r'^(?P<app_name>app|deezer)/profile/(?P<user_id>\S+)/$', WebAppView.as_view(), {'page': 'profile'}, name='webapp_profile'),
    url(r'^(?P<app_name>app|deezer)/legal/$', WebAppView.as_view(), {'page': 'legal'}, name='webapp_legal'),
    url(r'^(?P<app_name>app|deezer)/contact/$', WebAppView.as_view(), {'page': 'contact'}, name='webapp_contact'),
    url(r'^(?P<app_name>app|deezer)/about/$', WebAppView.as_view(), {'page': 'about'}, name='webapp_about'),
    url(r'^(?P<app_name>app|deezer)/jobs/$', WebAppView.as_view(), {'page': 'jobs'}, name='webapp_jobs'),
    url(r'^(?P<app_name>app|deezer)/help/$', WebAppView.as_view(), {'page': 'help'}, name='webapp_help'),
    url(r'^(?P<app_name>app|deezer)/tutorial/$', WebAppView.as_view(), {'page': 'tutorial'}, name='webapp_tutorial'),
    url(r'^(?P<app_name>app|deezer)/press/$', WebAppView.as_view(), {'page': 'press'}, name='webapp_press'),
    url(r'^(?P<app_name>app|deezer)/tpl/(?P<template_name>\S+)/$', 'load_template'),
    url(r'^(?P<app_name>app|deezer)/logout/$', 'logout'),
    url(r'^(?P<app_name>app|deezer)/selection/(?P<genre>\w+)/$', WebAppView.as_view(), {'page': 'home'}, name='webapp'),

)
