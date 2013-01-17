from django.conf.urls.defaults import *

from django.conf.urls.defaults import *
from feeds import LatestPostFeed

urlpatterns = patterns('yablog.views',
    url(r'^$', 'posts'),
    url(r'^(?P<slug>[\w-]+)/$', 'posts'),
    # url(r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/(?P<slug>[-\w]+)/$', 'post', name='blog_post'),
)
