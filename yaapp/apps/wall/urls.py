from django.conf.urls.defaults import *
from models import Post

urlpatterns = patterns('wall.views',
  #(r'^latest/$', 'django.views.generic.date_based.archive_index', { 'queryset' : Post.objects.all(), 'date_field' : 'date', } ),
  (r'^all/$', 'all' ),
  (r'^write/$', 'write' ),
  (r'^sendpost/$', 'sendpost'),
  # API:
  (r'^allAPI/$', 'allAPI' ),
  (r'^sendpostAPI/$', 'sendpostAPI'),
)
