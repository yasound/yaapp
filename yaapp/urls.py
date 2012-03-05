from django.conf import settings

from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from tastypie.api import Api
from yabase.api import RadioNextSongsResource, RadioWallEventResource, \
    SongMetadataResource, SongInstanceResource, PlaylistResource, \
    RadioResource, SelectedRadioResource, FavoriteRadioResource, FriendRadioResource,\
    RadioLikerResource, RadioFavoriteResource, SearchRadioResource, SearchRadioByUserResource, SearchRadioBySongResource, \
    RadioCurrentUserResource, \
    WallEventResource, RadioUserResource, SongUserResource, NextSongResource, RadioEnabledPlaylistResource, \
    RadioAllPlaylistResource, LeaderBoardResource, MatchedSongResource, SearchSongResource, EditSongResource
from account.api import UserResource, LoginResource, SignupResource, LoginSocialResource
from account.friend_api import FriendResource
from stats.api import RadioListeningStatResource
from yabase.models import Radio
from os import path
# Uncomment the next two lines to enable the admin:
admin.autodiscover()

api = Api(api_name='v1')
#api.register(SongMetadataResource())
api.register(SongInstanceResource())
api.register(PlaylistResource())
api.register(UserResource())
api.register(RadioResource())
api.register(SearchRadioResource())
api.register(SearchRadioByUserResource())
api.register(SearchRadioBySongResource())
api.register(SelectedRadioResource())
api.register(FavoriteRadioResource())
api.register(FriendRadioResource())
api.register(WallEventResource())
api.register(LoginResource())
api.register(SignupResource())
api.register(LoginSocialResource())
api.register(NextSongResource())
api.register(FriendResource())
api.register(RadioListeningStatResource())
api.register(LeaderBoardResource())
api.register(SearchSongResource())
api.register(EditSongResource())

radio_next_songs = RadioNextSongsResource()
wall_event = RadioWallEventResource()
radio_likers = RadioLikerResource()
radio_favorites = RadioFavoriteResource()
current_users = RadioCurrentUserResource()
radio_user = RadioUserResource()
song_user = SongUserResource()
radio_enabled_playlist = RadioEnabledPlaylistResource()
radio_all_playlist = RadioAllPlaylistResource()
playlist_matched_songs = MatchedSongResource()

Radio.objects.unlock_all()

js_info_dict = {
    'packages': ('yabackoffice',),
}

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
    url(r'^api/v1/radio/(?P<radio_id>\d+)/playlist/(?P<playlist_index>\d+)/add_song/(?P<yasound_song_id>\d+)/$', 'yabase.views.add_song'),
    url(r'^api/v1/upload_song/(?P<song_id>\d+)/$', 'yabase.views.upload_song'),
    url(r'^api/v1/upload_song/$', 'yabase.views.upload_song'),
    url(r'^api/v1/upload_song_ajax/$', 'yabase.views.upload_song_ajax'),
    url(r'^api/v1/radio/(?P<radio_id>\d+)/playlists_update/$', 'yabase.views.upload_playlists'),
    url(r'^api/v1/task/(?P<task_id>\S+)/$', 'yabase.views.task_status'),
    url(r'^api/v1/user/(?P<user_id>\d+)/picture/$', 'account.views.set_user_picture'),
    url(r'^api/v1/radio/(?P<radio_id>\d+)/picture/$', 'yabase.views.set_radio_picture'),
    url(r'^api/v1/radio/(?P<radio_id>\d+)/liker/$', 'yabase.views.like_radio'),
    url(r'^api/v1/radio/(?P<radio_id>\d+)/neutral/$', 'yabase.views.neutral_radio'),
    url(r'^api/v1/radio/(?P<radio_id>\d+)/disliker/$', 'yabase.views.dislike_radio'),
    url(r'^api/v1/radio/(?P<radio_id>\d+)/favorite/$', 'yabase.views.favorite_radio'),
    url(r'^api/v1/radio/(?P<radio_id>\d+)/not_favorite/$', 'yabase.views.not_favorite_radio'),
    url(r'^api/v1/radio/(?P<radio_id>\d+)/favorite_song/$', 'yabase.views.add_song_to_favorites'),
    url(r'^api/v1/radio/(?P<radio_id>\S+)/get_next_song/$', 'yabase.views.get_next_song'),
    (r'^api/v1/radio/(?P<radio>\d+)/', include(radio_next_songs.urls)),
    (r'^api/v1/radio/(?P<radio>\d+)/', include(wall_event.urls)),
    (r'^api/v1/radio/(?P<radio>\d+)/', include(radio_likers.urls)),
    (r'^api/v1/radio/(?P<radio>\d+)/', include(radio_favorites.urls)),
    (r'^api/v1/radio/(?P<radio>\d+)/', include(current_users.urls)),
    (r'^api/v1/radio/(?P<radio>\d+)/', include(radio_enabled_playlist.urls)),
    (r'^api/v1/radio/(?P<radio>\d+)/', include(radio_all_playlist.urls)),
    (r'^api/v1/playlist/(?P<playlist>\d+)/', include(playlist_matched_songs.urls)),
    (r'^api/v1/', include(radio_user.urls)),
    (r'^api/v1/', include(song_user.urls)),
    url(r'^api/v1/song/(?P<song_id>\d+)/liker/$', 'yabase.views.like_song'),
    url(r'^api/v1/song/(?P<song_id>\d+)/neutral/$', 'yabase.views.neutral_song'),
    url(r'^api/v1/song/(?P<song_id>\d+)/disliker/$', 'yabase.views.dislike_song'),
    url(r'^api/v1/song/(?P<song_id>\d+)/status/$', 'yabase.views.get_song_status'),
    url(r'^api/v1/subscription/$', 'account.views.get_subscription'),
    url(r'^api/v1/radio/(?P<radio_uuid>\S+)/start_listening/$', 'yabase.views.start_listening_to_radio'),
    url(r'^api/v1/radio/(?P<radio_uuid>\S+)/stop_listening/$', 'yabase.views.stop_listening_to_radio'),
    url(r'^api/v1/radio/(?P<radio_id>\d+)/connect/$', 'yabase.views.connect_to_radio'),
    url(r'^api/v1/radio/(?P<radio_id>\d+)/disconnect/$', 'yabase.views.disconnect_from_radio'),
    url(r'^api/v1/radio/(?P<radio_id>\d+)/current_song/$', 'yabase.views.get_current_song'),
    (r'^api/', include(api.urls)),
    (r'^listen/(?P<radio_uuid>[\w-]+.*[\w-]*)', 'yabase.views.web_listen'),
    url(r'^graph/radio/(?P<radio_id>\d+)/song/(?P<song_id>\d+)', 'yagraph.views.song_graph'),

    # web front end
    url(r'^$', 'yabase.views.web_index', name='web_index'),
    url(r'^radios/my/$', 'yabase.views.web_myradio', name='web_myradio'),
    url(r'^radios/friends/$', 'yabase.views.web_friends', name='web_friends'),
    url(r'^radios/favorites/$', 'yabase.views.web_favorites', name='web_favorites'),
    url(r'^radios/favorites/(?P<radio_uuid>[\w-]+.*[\w-]*)$', 'yabase.views.web_favorite', name='web_favorite'),
    url(r'^radios/selection/$', 'yabase.views.web_selections', name='web_selections'),
    url(r'^terms/$', 'yabase.views.web_terms', name='web_terms'),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {"next_page": "/"}, name="logout"),
    
    url(r'^radio/(?P<radio_id>\d+)/unmatched/$', 'yabase.views.radio_unmatched_song'),
        
    # yaref (fuzzy, ..)
    (r'^yaref/', include('yaref.urls')),
    (r'^yabackoffice/', include('yabackoffice.urls')),
    (r'^invitation/', include('yainvitation.urls')),
    (r'^jsi18n/$', 'django.views.i18n.javascript_catalog', js_info_dict),
    
    url(r'', include('social_auth.urls')),
    url(r'^login/$', 'account.views.login', name="login"),
    url(r'^login-error/$', 'account.views.error', name='login-error'),
)

if settings.LOCAL_MODE:
    urlpatterns += patterns('',

    # if we are in local mode we need django to serve medias
     (r'^media/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': path.join(settings.PROJECT_PATH, 'media')}),

    )
