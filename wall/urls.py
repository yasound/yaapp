from django.conf.urls.defaults import *
from yaapp.wall.models import Post

urlpatterns = patterns('',
  #(r'^latest/$', 'django.views.generic.date_based.archive_index', { 'queryset' : Post.objects.all(), 'date_field' : 'date', } ),
  (r'^all/$', 'yaapp.wall.views.all' ),
  (r'^write/$', 'yaapp.wall.views.write' ),
  (r'^sendpost/$', 'yaapp.wall.views.sendpost'),
)
