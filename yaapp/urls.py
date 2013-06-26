from account.api import UserResource, LoginResource, SignupResource, \
    PublicUserResource, PopularUserResource, LoginSocialResource
from account.friend_api import FriendResource
from django.conf import settings
from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from django.views.generic.simple import direct_to_template
from os import path
from stats.api import RadioListeningStatResource
from tastypie.api import Api
from yabase.api import RadioNextSongsResource, RadioWallEventResource, \
    SongMetadataResource, SongInstanceResource, ProgrammingResource, PlaylistResource, \
    PublicRadioResource, RadioResource, SelectedRadioResource, \
    SelectedWebRadioResource, TopRadioResource, \
    FavoriteRadioResource, FriendRadioResource, TechTourRadioResource, \
    RadioLikerResource, RadioFavoriteResource, SearchRadioResource, \
    SearchRadioByUserResource, SearchRadioBySongResource, RadioCurrentUserResource, \
    WallEventResource, RadioUserResource, SongUserResource, NextSongResource, \
    RadioEnabledPlaylistResource, RadioAllPlaylistResource, LeaderBoardResource, \
    MatchedSongResource, SearchSongResource, EditSongResource, \
    UserFavoriteRadioResource
from yabase.models import Radio
from yaweb import urls as yaweb_urls
from yaweb.sitemap import StaticSitemap
from yabase.sitemap import WebappSiteMap
from yablog.sitemaps import BlogPostSitemap
from yablog.feeds import LatestPostFeed
# Uncomment the next two lines to enable the admin:
admin.autodiscover()

api = Api(api_name='v1')
#api.register(SongMetadataResource())
api.register(SongInstanceResource())
api.register(PlaylistResource())
api.register(UserResource())
api.register(PublicUserResource())
api.register(PopularUserResource())
api.register(RadioResource())
api.register(PublicRadioResource())
api.register(SearchRadioResource())
api.register(SearchRadioByUserResource())
api.register(SearchRadioBySongResource())
api.register(SelectedWebRadioResource())
api.register(SelectedRadioResource())
api.register(TopRadioResource())
api.register(FavoriteRadioResource())
api.register(FriendRadioResource())
api.register(TechTourRadioResource())
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

radio_user = RadioUserResource()
song_user = SongUserResource()
radio_enabled_playlist = RadioEnabledPlaylistResource()
radio_all_playlist = RadioAllPlaylistResource()
playlist_matched_songs = MatchedSongResource()

user_favorite_radios = UserFavoriteRadioResource()

js_info_dict = {
    'packages': ('yabackoffice', 'yabase',),
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
    url(r'^api/v1/radio_slug/(?P<radio_uuid_or_slug>[\w-]+)/$', 'yabase.views.radio'),
    url(r'^api/v1/radio/(?P<radio_id>\d+)/playlist/(?P<playlist_index>\d+)/add_song/(?P<yasound_song_id>\d+)/$', 'yabase.views.add_song'),
    url(r'^api/v1/upload_song/(?P<song_id>\d+)/$', 'yabase.views.upload_song'),
    url(r'^api/v1/upload_song/$', 'yabase.views.upload_song'),
    url(r'^api/v1/upload_song_ajax/$', 'yabase.views.upload_song_ajax'),
    url(r'^api/v1/radio/(?P<radio_id>\d+)/playlists_update/$', 'yabase.views.upload_playlists'),
    url(r'^api/v1/task/(?P<task_id>\S+)/$', 'yabase.views.task_status'),
    url(r'^api/v1/user/(?P<user_id>\d+)/picture/$', 'account.views.set_user_picture'),
    url(r'^api/v1/user/(?P<user_id>\d+)/', include(user_favorite_radios.urls)),

    url(r'^api/v1/user/(?P<username>\S+)/favorites/$', 'yabase.views.user_favorites'),
    url(r'^api/v1/user/(?P<username>\S+)/friends/$', 'account.views.user_friends'),
    url(r'^api/v1/user/(?P<username>\S+)/followers/$', 'account.views.user_followers'),
    url(r'^api/v1/user/(?P<username>\S+)/likes/$', 'account.views.user_likes'),
    url(r'^api/v1/user/(?P<username>\S+)/picture/$', 'account.views.user_picture', {'size': 'large'}),
    url(r'^api/v1/user/(?P<username>\S+)/picture/xl/$', 'account.views.user_picture', {'size': 'xl'}),
    url(r'^api/v1/user/(?P<username>\S+)/picture/xs/$', 'account.views.user_picture', {'size': 'xs'}, name='user_small_picture'),
    url(r'^api/v1/user/(?P<username>\S+)/picture/(?P<size>\w+)/$', 'account.views.user_picture', name='user_custom_picture'),

    url(r'^api/v1/my_profile/$', 'account.views.my_profile'),
    url(r'^api/v1/logout/$', 'account.views.logout_current_user'),

    # activity
    url(r'^api/v1/friends_activity/$', 'yaactivity.views.friends_activity'),
    url(r'^api/v1/radios_activity/$', 'yaactivity.views.radios_activity'),

    url(r'^api/v1/followers/$', 'account.views.user_followers'),
    url(r'^api/v1/user/(?P<username>\S+)/friends/(?P<friend>\S+)/$', 'account.views.user_friends_add_remove'),
    url(r'^api/v1/user/(?P<username>\S+)/radios/$', 'yabase.views.user_radios'),
    url(r'^api/v1/radio/(?P<radio_id>\d+)/picture/$', 'yabase.views.set_radio_picture'),
    url(r'^api/v1/radio/(?P<radio_id>\d+)/liker/$', 'yabase.views.like_radio'),
    url(r'^api/v1/radio/(?P<radio_id>\d+)/neutral/$', 'yabase.views.neutral_radio'),
    url(r'^api/v1/radio/(?P<radio_id>\d+)/disliker/$', 'yabase.views.dislike_radio'),
    url(r'^api/v1/radio/(?P<radio_id>\d+)/favorite/$', 'yabase.views.favorite_radio'),
    url(r'^api/v1/radio/(?P<radio_id>\d+)/not_favorite/$', 'yabase.views.not_favorite_radio'),
    url(r'^api/v1/radio/(?P<radio_id>\d+)/shared/$', 'yabase.views.radio_shared'),
    url(r'^api/v1/radio/(?P<radio_id>\d+)/favorite_song/$', 'yabase.views.add_song_to_favorites'),
    url(r'^api/v1/radio/(?P<radio_id>\S+)/get_next_song/$', 'yabase.views.get_next_song'),
    url(r'^api/v1/radio/(?P<radio_id>\S+)/post_message/$', 'yabase.views.post_message'),
    (r'^api/v1/radio/(?P<radio>\d+)/', include(radio_next_songs.urls)),
    (r'^api/v1/radio/(?P<radio>\d+)/', include(wall_event.urls)),
    (r'^api/v1/radio/(?P<radio>\d+)/', include(radio_likers.urls)),
    (r'^api/v1/radio/(?P<radio>\d+)/', include(radio_favorites.urls)),
    (r'^api/v1/radio/(?P<radio>\d+)/', include(radio_enabled_playlist.urls)),
    (r'^api/v1/radio/(?P<radio>\d+)/', include(radio_all_playlist.urls)),
    (r'^api/v1/playlist/(?P<playlist>\d+)/', include(playlist_matched_songs.urls)),
    (r'^api/v1/', include(radio_user.urls)),
    (r'^api/v1/', include(song_user.urls)),
    url(r'^api/v1/song/(?P<song_id>\d+)/liker/$', 'yabase.views.like_song'),
    url(r'^api/v1/song/(?P<song_id>\d+)/neutral/$', 'yabase.views.neutral_song'),
    url(r'^api/v1/song/(?P<song_id>\d+)/disliker/$', 'yabase.views.dislike_song'),
    url(r'^api/v1/song/(?P<song_id>\d+)/status/$', 'yabase.views.get_song_status'),
    url(r'^api/v1/song/(?P<song_id>\d+)/download_preview/$', 'yabase.views.download_preview'),
    url(r'^api/v1/subscription/$', 'account.views.get_subscription'),

    # live
    url(r'^api/v1/radio/(?P<radio_uuid>[\w-]+)/live/$', 'yabase.views.radio_live'),

    # show songs
    url(r'^api/v1/show/(?P<show_id>\S+)/songs/$', 'yashow.views.get_songs_for_show'),
    url(r'^api/v1/show/(?P<show_id>\S+)/add_song/(?P<yasound_song_id>\d+)/$', 'yashow.views.add_song_in_show'),
    url(r'^api/v1/show/(?P<show_id>\S+)/remove_song/(?P<song_instance_id>\d+)/$', 'yashow.views.remove_song_from_show'),
    # shows
    url(r'^api/v1/show/(?P<show_id>\S+)/duplicate/$', 'yashow.views.duplicate_show'),
    url(r'^api/v1/show/(?P<show_id>\S+)/$', 'yashow.views.show'),
    url(r'^api/v1/radio/(?P<radio_uuid>[\w-]+)/create_show/$', 'yashow.views.create_show'),
    url(r'^api/v1/radio/(?P<radio_uuid>[\w-]+)/shows/$', 'yashow.views.get_shows_for_radio'),


    url(r'^api/v1/radio/(?P<radio_uuid>[\w-]+)/broadcast_message/$', 'yabase.views.radio_broadcast_message'),
    url(r'^api/v1/radio/(?P<radio_uuid>[\w-]+)/start_listening/$', 'yabase.views.start_listening_to_radio'),
    url(r'^api/v1/radio/(?P<radio_uuid>[\w-]+)/stop_listening/$', 'yabase.views.stop_listening_to_radio'),
    url(r'^api/v1/radio/(?P<radio_uuid>[\w-]+)/stopped/$', 'yabase.views.radio_has_stopped'),
    url(r'^api/v1/radio/(?P<radio_uuid>[\w-]+)/song/(?P<songinstance_id>\d+)/played/$', 'yabase.views.song_played'),
    url(r'^api/v1/radio/(?P<radio_id>\d+)/connect/$', 'yabase.views.connect_to_radio'),
    url(r'^api/v1/radio/(?P<radio_id>\d+)/disconnect/$', 'yabase.views.disconnect_from_radio'),
    url(r'^api/v1/radio/(?P<radio_id>\d+)/current_song/$', 'yabase.views.get_current_song'),
    url(r'^api/v1/radio/(?P<radio_id>\d+)/buy_link/$', 'yabase.views.buy_link', name='buy_link'),
    url(r'^api/v1/radio/(?P<radio_uuid>[\w-]+)/similar/$', 'yabase.views.similar_radios', name='similar_radios'),
    url(r'^api/v1/radio/(?P<radio_uuid>[\w-]+)/likes/$', 'yabase.views.radio_likes', name='radio_likes'),
    url(r'^api/v1/song_instance/(?P<song_instance_id>\d+)/cover/$', 'yabase.views.song_instance_cover'),
    url(r'^api/v1/account/association/$', 'account.views.associate'),
    url(r'^api/v1/account/dissociation/$', 'account.views.dissociate'),

    url(r'^api/v1/songs_started/$', 'yabase.views.songs_started'),

    # programming
    url(r'^api/v1/radio/(?P<radio_uuid>[\w-]+)/programming/$', 'yabase.views.my_programming'),
    url(r'^api/v1/radio/(?P<radio_uuid>[\w-]+)/programming/(?P<song_instance_id>\d+)/$', 'yabase.views.my_programming'),
    url(r'^api/v1/radio/(?P<radio_uuid>[\w-]+)/programming/artists/$', 'yabase.views.my_programming_artists'),
    url(r'^api/v1/radio/(?P<radio_uuid>[\w-]+)/programming/albums/$', 'yabase.views.my_programming_albums'),
    url(r'^api/v1/radio/(?P<radio_uuid>[\w-]+)/programming/yasound_songs/$', 'yabase.views.my_programming_yasound_songs'),
    url(r'^api/v1/radio/(?P<radio_uuid>[\w-]+)/programming/status/$', 'yabase.views.my_programming_status'),
    url(r'^api/v1/radio/(?P<radio_uuid>[\w-]+)/programming/status/(?P<event_id>\S+)/$', 'yabase.views.my_programming_status'),
    url(r'^api/v1/programming/status/(?P<event_id>\S+)/$', 'yabase.views.programming_status_details'),

    # new wall system
    url(r'^api/v1/radio/(?P<radio_uuid>[\w-]+)/wall/$', 'yawall.views.wall'),
    url(r'^api/v1/radio/(?P<radio_uuid>[\w-]+)/wall/(?P<event_id>\S+)/$', 'yawall.views.wall'),
    url(r'^api/v1/wall/(?P<event_id>\S+)/report_as_abuse/$', 'yawall.views.report_event_as_abuse'),

    # pictures
    url(r'^api/v1/radio/(?P<radio_uuid>[\w-]+)/picture/$', 'yabase.views.radio_picture'),
    url(r'^api/v1/radio/(?P<radio_uuid>[\w-]+)/picture/xl/$', 'yabase.views.radio_picture', {'size': 'xl'}),
    url(r'^api/v1/radio/(?P<radio_uuid>[\w-]+)/picture/xs/$', 'yabase.views.radio_picture', {'size': 'xs'}, name='radio_small_picture'),
    url(r'^api/v1/radio/(?P<radio_uuid>[\w-]+)/picture/(?P<size>\w+)/$', 'yabase.views.radio_picture', name='radio_custom_picture'),
    url(r'^api/v1/radio/(?P<radio_uuid>[\w-]+)/wall_layout/$', 'yabase.views.wall_layout'),


    url(r'^api/v1/user/(?P<username>\S+)/picture/$', 'account.views.user_picture'),

    # jingles
    url(r'^api/v1/jingle/', include('yajingle.urls')),

    # listeners
    url(r'^api/v1/radio/(?P<radio_uuid_or_slug>[\w-]+)/listeners/$', 'yabase.views.listeners', name='listeners'),
    url(r'^api/v1/radio/(?P<radio_uuid_or_slug>[\w-]+)/favorites/$', 'yabase.views.fans', name='fans'),
    url(r'^api/v1/radio/(?P<radio_id>\d+)/current_user/$', 'yabase.views.listeners_legacy', name='listeners_legacy'),


    url(r'^api/v1/search/radios/$', 'yasearch.views.search_songs_in_radios'),
    url(r'^api/v1/search/in_radios/$', 'yasearch.views.search_radios'),


    # misc
    url(r'^api/v1/user_watched_tutorial/$', 'yabase.views.user_watched_tutorial'),

    # song download for deezer
    url(r'^api/v1/radio/(?P<radio_uuid>[\w-]+)/gdu/$', 'yabase.views.generate_download_current_song_url'),
    url(r'^api/v1/radio/(?P<radio_uuid>[\w-]+)/d/(?P<token>\S+)/$', 'yabase.views.download_current_song', name='download_current_song'),

    # api (will override any other url)
    (r'^api/', include(api.urls)),
    url(r'^graph/radio/(?P<radio_id>\d+)/song/(?P<song_id>\d+)', 'yagraph.views.song_graph'),
    (r'^status/', 'yabase.views.status'),

    url(r'^api/v1/delete_song/(?P<song_instance_id>\d+)/$', 'yabase.views.delete_song_instance'),
    url(r'^api/v1/delete_message/(?P<message_id>\d+)/$', 'yabase.views.delete_message'),
    url(r'^api/v1/report_message/(?P<message_id>\d+)/$', 'yabase.views.report_message_as_abuse'),

    url(r'^api/v1/notify_missing_song/$', 'yabase.views.notify_missing_song'),

    url(r'^api/v1/reject_song/(?P<song_id>\d+)/$', 'yabase.views.reject_song'),

    url(r'^api/v1/most_active_radio/$', 'yabase.views.most_active_radios'),

    url(r'^api/v1/ping/$', 'yabase.views.ping'),

    url(r'^api/v1/public_stats/$', 'yabase.views.public_stats'),
    url(r'^api/v1/my_radios/$', 'yabase.views.my_radios'),
    url(r'^api/v1/my_radios/(?P<radio_uuid>[\w-]+)/$', 'yabase.views.my_radios'),


    url(r'^api/v1/ios_push_notif_token/$', 'account.views.send_ios_push_notif_token'),
    url(r'^api/v1/notifications_preferences/$', 'account.views.get_notifications_preferences'),
    url(r'^api/v1/set_notifications_preferences/$', 'account.views.set_notifications_preferences'),

    url(r'^api/v1/facebook_share_preferences/$', 'account.views.get_facebook_share_preferences'),
    url(r'^api/v1/set_facebook_share_preferences/$', 'account.views.set_facebook_share_preferences'),

    url(r'^api/v1/twitter_share_preferences/$', 'account.views.get_twitter_share_preferences'),
    url(r'^api/v1/set_twitter_share_preferences/$', 'account.views.set_twitter_share_preferences'),

    # streamer auth token
    url(r'^api/v1/streamer_auth_token/$', 'account.views.get_streamer_auth_token'),
    url(r'^api/v1/check_streamer_auth_token/(?P<token>\S+)/$', 'account.views.check_streamer_auth_token'),

    # notifications
    url(r'^api/v1/notifications/$', 'yamessage.views.get_notifications'),
    url(r'^api/v1/notification/(?P<notif_id>\S+)/$', 'yamessage.views.get_notification'),
    url(r'^api/v1/update_notification/(?P<notif_id>\S+)/$', 'yamessage.views.update_notification'),
    url(r'^api/v1/delete_notification/(?P<notif_id>\S+)/$', 'yamessage.views.delete_notification'),
    url(r'^api/v1/delete_all_notifications/$', 'yamessage.views.delete_all_notifications'),
    url(r'^api/v1/notifications/mark_all_as_read/$', 'yamessage.views.mark_all_as_read'),
    url(r'^api/v1/notifications/unread_count/$', 'yamessage.views.unread_count'),

    url(r'^api/v1/radio_recommendations/$', 'yabase.views.radio_recommendations'),

    # friends invitation
    url(r'^api/v1/invite_ios_contacts/$', 'account.views.invite_ios_contacts'),
    url(r'^api/v1/invite_email_friends/$', 'account.views.invite_email_friends'),
    url(r'^api/v1/invite_facebook_friends/$', 'account.views.invite_facebook_friends'),
    url(r'^api/v1/invite_twitter_friends/$', 'account.views.invite_twitter_friends'),


    # web front end
    #url(r'^$', 'yaweb.views.stay_tuned', name='index'),

    # special case for iOS client
    url(r'^legal/eula.html$', 'yaweb.views.eula', name='eula'),
    url(r'^legal/privacy.html$', 'yaweb.views.privacy', name='privacy'),
    url(r'^fr/images/logo.png$', 'yaweb.views.logo', name='logo'),

    url(r'^', include('yaweb.urls')),

    (r'^listen/(?P<radio_uuid_or_slug>[\w-]+.*[\w-]*)/(?P<song_instance_id>\d+)$', 'yabase.views.web_song'),
    (r'^listen/(?P<radio_uuid_or_slug>[\w-]+.*[\w-]*)$', 'yabase.views.web_listen'),
    (r'^widget/(?P<radio_uuid_or_slug>[\w-]+.*[\w-]*)/$', 'yabase.views.web_widget'),
    (r'^widget/(?P<radio_uuid_or_slug>[\w-]+.*[\w-]*)/(?P<wtype>\S+)', 'yabase.views.web_widget'),

    (r'^social_widget/(?P<radio_uuid_or_slug>[\w-]+)/$', 'yabase.views.web_social_widget'),
    (r'^social_widget/(?P<radio_uuid_or_slug>[\w-]+)/login/$', 'yabase.views.web_social_widget_login'),
    (r'^social_widget/(?P<radio_uuid_or_slug>[\w-]+)/signup/$', 'yabase.views.web_social_widget_signup'),

    url(r'^buy_unavailable/$', 'yabase.views.buy_link_not_found', name='buy_link_not_found'),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {"next_page": "/"}, name="logout"),

    # yapremium
    (r'^api/v1/premium/', include('yapremium.urls')),

    # blog
    (r'^api/v1/blog/', include('yablog.urls')),
    url(r'^news/rss/$',  LatestPostFeed(), name='blog_post_rss'),

    # yaref (fuzzy, ..)
    (r'^yaref/', include('yaref.urls')),
    (r'^yabackoffice/', include('yabackoffice.urls')),
    (r'^invitation/', include('yainvitation.urls')),

    (r'^i18n/', include('django.conf.urls.i18n')),
    (r'^jsi18n/$', 'django.views.i18n.javascript_catalog', js_info_dict),

    url(r'', include('social_auth.urls')),
    #url(r'^login/$', 'account.views.login', name="login"),
    #url(r'^signup/$', 'account.views.signup', name="signup"),
    url(r'^login-error/$', 'account.views.error', name='login-error'),
    url(r'^passreset/$','account.views.password_reset', name='lost_password'),
    url(r'^passresetconfirm/(?P<uidb36>[-\w]+)/(?P<token>[-\w]+)/$','account.views.password_reset_confirm', name='reset_password_confirm'),

    url(r'^api/v1/set_localization/$','account.views.update_localization'),

    url(r'^api/v1/connected_users/$','account.views.connected_users_by_distance'),
    url(r'^api/v1/fast_connected_users/$','account.views.fast_connected_users_by_distance'),


    url(r'^api/v2/radio/(?P<radio_uuid>[\w-]+)/leaderboard/$', 'yabase.views.radio_leaderboard', name='radio_leaderboard'),

    # facebook update notification
    url(r'^facebook_update/$', 'account.views.facebook_update', name='facebook_update'),

    # tapjoy callback
    url(r'^tapjoy_callback/$', 'yapremium.views.tapjoy_callback', name='tapjoy_callback'),


    #email confirmation
    (r'^confirm_email/(\w+)/$', 'emailconfirmation.views.confirm_email'),

    #yamenu
    (r'^api/v1/app_menu/$', 'yamenu.views.menu_description'),

    # newsletters
    url(r'^newsletters/', include('emencia.django.newsletter.urls')),

    # internal stuff
    url(r'^internal/user_authenticated/$', 'account.views.user_authenticated', name='user_authenticated'),

    url(r'^internal/songs/$', 'yaref.views.internal_songs'),
    url(r'^internal/songs/(?P<song_id>\d+)/$', 'yaref.views.internal_songs'),
    url(r'^internal/songs/download/(?P<song_id>\d+)/$', 'yaref.views.internal_song_download'),


    url(r'^deezer/close/$', 'yabase.views.close', name='close'),
    url(r'^login/close/$', 'yabase.views.close', name='login_close'),

    (r'^attachments/', include('attachments.urls')),

    (r'^', include('yabase.urls')),

    # deezer
    url(r'^', include('yadeezer.urls')),

)

if settings.PRODUCTION_MODE:
    urlpatterns += patterns('',
        url(r'^robots\.txt$', direct_to_template, {'template': 'robots.txt', 'mimetype': 'text/plain'}),
        url(r'^9EE008A3E4D3EDCC2AFD49389AC54723\.txt$', direct_to_template, {'template': '9EE008A3E4D3EDCC2AFD49389AC54723.txt', 'mimetype': 'text/plain'}),
        url(r'^channel\.html$', direct_to_template, {'template': 'facebook_channel.html', 'mimetype': 'text/html'}, name='facebook_channel_url'),
        url(r'^deezer/facebook_channel\.html$', direct_to_template, {'template': 'facebook_channel.html', 'mimetype': 'text/html'}, name='deezer_facebook_channel_url'),
    )
else:
    urlpatterns += patterns('',
        url(r'^robots\.txt$', direct_to_template, {'template': 'robots.forbidden.txt', 'mimetype': 'text/plain'}),
        url(r'^9EE008A3E4D3EDCC2AFD49389AC54723\.txt$', direct_to_template, {'template': '9EE008A3E4D3EDCC2AFD49389AC54723.txt', 'mimetype': 'text/plain'}),
        url(r'^channel\.html$', direct_to_template, {'template': 'facebook_channel.html', 'mimetype': 'text/html'}, name='facebook_channel_url'),
        url(r'^deezer/facebook_channel\.html$', direct_to_template, {'template': 'facebook_channel.html', 'mimetype': 'text/html'}, name='deezer_facebook_channel_url'),
    )

# sitemap
sitemaps = {
    'yaapp': WebappSiteMap(),
    'blog': BlogPostSitemap(),
}

urlpatterns += patterns('django.contrib.sitemaps.views',
    (r'^sitemap\.xml$', 'sitemap', {'sitemaps': sitemaps}),
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

if settings.LOCAL_MODE or settings.DEVELOPMENT_MODE:
    urlpatterns += patterns('',
        (r'^profiling/$', 'yabase.views.profiling'),
    )
