from django.conf import settings

from django.views.generic.simple import direct_to_template
from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from tastypie.api import Api
from yabase.api import RadioNextSongsResource, RadioWallEventResource, \
    SongMetadataResource, SongInstanceResource, PlaylistResource, \
    RadioResource, SelectedRadioResource, TopRadioResource, FavoriteRadioResource, FriendRadioResource,\
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
api.register(TopRadioResource())
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

#Radio.objects.unlock_all()

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
    (r'^rahadm/', include(admin.site.urls)),
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
    url(r'^api/v1/radio/(?P<radio_id>\d+)/buy_link/$', 'yabase.views.buy_link', name='buy_link'),
    url(r'^api/v1/song_instance/(?P<song_instance_id>\d+)/cover/$', 'yabase.views.song_instance_cover'),
    url(r'^api/v1/account/associate/$', 'account.views.associate'),
    url(r'^api/v1/account/dissociate/$', 'account.views.dissociate'),
    (r'^api/', include(api.urls)),
    url(r'^graph/radio/(?P<radio_id>\d+)/song/(?P<song_id>\d+)', 'yagraph.views.song_graph'),
    (r'^status/', 'yabase.views.status'),

    # web front end
    url(r'^$', 'yaweb.views.index', name='index'),
    
    # special case for iOS client
    url(r'^legal/eula.html$', 'yaweb.views.eula', name='eula'),
    url(r'^fr/images/logo.png$', 'yaweb.views.logo', name='logo'),
    
    url(r'^', include('yaweb.urls')),

    (r'^listen/(?P<radio_uuid>[\w-]+.*[\w-]*)', 'yabase.views.web_listen'),
    url(r'^buy_unavailable/$', 'yabase.views.buy_link_not_found', name='buy_link_not_found'),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {"next_page": "/"}, name="logout"),
    
    # yaref (fuzzy, ..)
    (r'^yaref/', include('yaref.urls')),
    (r'^yabackoffice/', include('yabackoffice.urls')),
    (r'^invitation/', include('yainvitation.urls')),
    
    (r'^i18n/', include('django.conf.urls.i18n')),
    (r'^jsi18n/$', 'django.views.i18n.javascript_catalog', js_info_dict),
    
    url(r'', include('social_auth.urls')),
    url(r'^login/$', 'account.views.login', name="login"),
    url(r'^login-error/$', 'account.views.error', name='login-error'),
    url(r'^passreset/$','account.views.password_reset', name='lost_password'),
    url(r'^passresetconfirm/(?P<uidb36>[-\w]+)/(?P<token>[-\w]+)/$','account.views.password_reset_confirm', name='reset_password_confirm'),

    # facebook update notification
    url(r'^facebook_update/$', 'account.views.facebook_update', name='facebook_update'),
    
    #email confirmation
    (r'^confirm_email/(\w+)/$', 'emailconfirmation.views.confirm_email'),
     
    (r'^robots\.txt$', direct_to_template,
     {'template': 'robots.txt', 'mimetype': 'text/plain'}),
)

# captcha urls
urlpatterns += patterns('',
    url(r'^captcha/', include('captcha.urls')),
)

if settings.LOCAL_MODE:
    urlpatterns += patterns('',

    # if we are in local mode we need django to serve medias
     (r'^media/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': path.join(settings.PROJECT_PATH, 'media')}),

    )
