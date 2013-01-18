from django.conf.urls.defaults import *

urlpatterns = patterns('yafaq.views',
   url(r'^$', 'entries'),
)
