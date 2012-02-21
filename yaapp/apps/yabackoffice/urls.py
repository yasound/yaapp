from django.conf.urls.defaults import *

urlpatterns = patterns('yabackoffice.views',
    url(r'^$', 'index', name='yabackoffice_index'),
)