from django.conf.urls.defaults import *

urlpatterns = patterns('yainvitation.views',
    url(r'^accept/(\w+)/$', 'accept', name='yainvitation_accept'),
)