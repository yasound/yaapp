from django.conf.urls.defaults import *

urlpatterns = patterns('yapremium.views',
    url(r'^subscriptions/$', 'subscriptions'),
    url(r'^subscriptions/(?P<subscription_sku>\S+)/$', 'subscriptions'),
    url(r'^services/$', 'services'),
    url(r'^gifts/$', 'gifts'),
)
