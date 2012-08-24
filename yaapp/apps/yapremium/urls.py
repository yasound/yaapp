from django.conf.urls.defaults import *

urlpatterns = patterns('yapremium.views',
    url(r'^subscriptions/$', 'subscriptions'),
    url(r'^subscriptions/(?P<subscription_id>\d+)$', 'subscriptions'),
)
