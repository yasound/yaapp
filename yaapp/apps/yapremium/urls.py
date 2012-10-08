from django.conf.urls.defaults import *

urlpatterns = patterns('yapremium.views',
    url(r'^subscriptions/$', 'subscriptions'),
    url(r'^subscriptions/(?P<subscription_sku>\S+)/$', 'subscriptions'),
    url(r'^services/$', 'services'),
    url(r'^gifts/$', 'gifts'),
    url(r'^actions_completed/watch_tutorial/(?P<username>\S+)/$', 'action_watch_tutorial_completed'),
    url(r'^actions_completed/follow_yasound_on_twitter/', 'action_follow_yasound_on_twitter_completed'),
    url(r'^follow_yasound_on_twitter/', 'action_follow_yasound_on_twitter'),
    url(r'^activate_promocode/$', 'activate_promocode'),
)
