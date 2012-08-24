from django.conf.urls.defaults import *

urlpatterns = patterns('yapremium.views',
    url(r'^premium/subscriptions/$', 'subscriptions'),
)
