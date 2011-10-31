from django.conf.urls.defaults import *
from yachat.wall.models import Post

urlpatterns = patterns('',
  #(r'^latest/$', 'django.views.generic.date_based.archive_index', { 'queryset' : Post.objects.all(), 'date_field' : 'date', } ),
  (r'^all/$', 'yachat.wall.views.all' ),
  (r'^write/$', 'yachat.wall.views.write' ),
  (r'^sendpost/$', 'yachat.wall.views.sendpost'),
)
