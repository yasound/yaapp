from django.conf.urls.defaults import *

urlpatterns = patterns('yaref.views',
    url(r'^find/$', 'find_fuzzy', name='yaref_find'),
)