from django.conf.urls.defaults import *

urlpatterns = patterns('yaref.views',
    url(r'^find.json/$', 'find_fuzzy_json', name='yaref_find_json'),
    url(r'^find/$', 'find_fuzzy', name='yaref_find'),
    url(r'^album/(?P<album_id>\d+)/cover/$', 'album_cover', name='yaref_album_cover'),
    url(r'^download_preview/(?P<id>\d+)/$', 'download_preview'),
)