from django.conf.urls.defaults import *

urlpatterns = patterns('yapremium.views',
    url(r'^subscriptions/$', 'subscriptions'),
    url(r'^subscriptions/(?P<subscription_sku>\S+)/$', 'subscriptions'),
    url(r'^services/$', 'services'),
    url(r'^gifts/$', 'gifts'),
    url(r'^actions_completed/watch_tutorial/(?P<username>\S+)/$', 'action_watch_tutorial_completed'),
    url(r'^activate_promocode/$', 'activate_promocode'),
)
