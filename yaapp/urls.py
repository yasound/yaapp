from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from tastypie.api import Api
from yabase.api import NextSongsResource, RadioWallEventResource, \
    SongMetadataResource, SongInstanceResource, PlaylistResource, \
    RadioResource, SelectedRadioResource, FavoriteRadioResource, FriendRadioResource,\
    RadioLikerResource, RadioUserConnectedResource, \
    PlayedSongResource, WallEventResource, RadioUserResource
from account.api import UserResource, LoginResource, SignupResource, LoginSocialResource

# Uncomment the next two lines to enable the admin:
admin.autodiscover()

api = Api(api_name='v1')
api.register(SongMetadataResource())
api.register(SongInstanceResource())
api.register(PlaylistResource())
api.register(UserResource())
api.register(RadioResource())
api.register(SelectedRadioResource())
api.register(FavoriteRadioResource())
api.register(FriendRadioResource())
api.register(WallEventResource())
api.register(LoginResource())
api.register(SignupResource())
api.register(LoginSocialResource())

next_songs = NextSongsResource()
wall_event = RadioWallEventResource()
radio_likers = RadioLikerResource()
connected_users = RadioUserConnectedResource()
played_song = PlayedSongResource()
radio_user = RadioUserResource()

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
    url(r'^api/v1/radio/(?P<radio_id>\d+)/playlists/$', 'yabase.views.upload_playlists'),
    url(r'^api/v1/task/(?P<task_id>\S+)/$', 'yabase.views.task_status'),
    url(r'^api/v1/user/(?P<user_id>\d+)/picture/$', 'account.views.set_user_picture'),
    url(r'^api/v1/radio/(?P<radio_id>\d+)/picture/$', 'yabase.views.set_radio_picture'),
    url(r'^api/v1/radio/(?P<radio_id>\d+)/likers/$', 'yabase.views.like_radio'),
    url(r'^api/v1/radio/(?P<radio_id>\d+)/neutral/$', 'yabase.views.neutral_radio'),
    url(r'^api/v1/radio/(?P<radio_id>\d+)/dislikers/$', 'yabase.views.dislike_radio'),
    url(r'^api/v1/radio/(?P<radio_id>\d+)/favorite/$', 'yabase.views.favorite_radio'),
    url(r'^api/v1/radio/(?P<radio_id>\d+)/not_favorite/$', 'yabase.views.not_favorite_radio'),
    (r'^api/v1/radio/(?P<radio>\d+)/', include(next_songs.urls)),
    (r'^api/v1/radio/(?P<radio>\d+)/', include(wall_event.urls)),
    (r'^api/v1/radio/(?P<radio>\d+)/', include(radio_likers.urls)),
    (r'^api/v1/radio/(?P<radio>\d+)/', include(connected_users.urls)),
    (r'^api/v1/radio/(?P<radio>\d+)/', include(played_song.urls)),
    (r'^api/v1/', include(radio_user.urls)),
    (r'^api/', include(api.urls)),
    # The normal jazz here, then...
)
