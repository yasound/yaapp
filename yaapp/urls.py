from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from tastypie.api import Api
from yabase.api import NextSongsResource, RadioWallEventResource, \
    SongMetadataResource, SongInstanceResource, PlaylistResource, \
    UserResource, RadioResource, RadioLikerResource, RadioUserConnectedResource, \
    PlayedSongResource, WallEventResource
# Uncomment the next two lines to enable the admin:
admin.autodiscover()

api = Api(api_name='v1')
api.register(SongMetadataResource())
api.register(SongInstanceResource())
api.register(PlaylistResource())
api.register(UserResource())
api.register(RadioResource())
api.register(WallEventResource())

next_songs = NextSongsResource()
wall_event = RadioWallEventResource()
radio_likers = RadioLikerResource()
connected_users = RadioUserConnectedResource()
played_song = PlayedSongResource()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'yaapp.views.home', name='home'),
    # url(r'^yaapp/', include('yaapp.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    #(r'^wall/', include('wall.urls')),
    (r'^admin/', include(admin.site.urls)),
    (r'^wall/', include('wall.urls')),
    (r'^api/v1/radio/(?P<radio>\d+)/', include(next_songs.urls)),
    (r'^api/v1/radio/(?P<radio>\d+)/', include(wall_event.urls)),
    (r'^api/v1/radio/(?P<radio>\d+)/', include(radio_likers.urls)),
    (r'^api/v1/radio/(?P<radio>\d+)/', include(connected_users.urls)),
    (r'^api/v1/radio/(?P<radio>\d+)/', include(played_song.urls)),                   
    (r'^api/', include(api.urls)),
    # The normal jazz here, then...
)
