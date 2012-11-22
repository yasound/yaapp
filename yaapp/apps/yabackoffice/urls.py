from django.conf.urls.defaults import *

urlpatterns = patterns('yabackoffice.views',
    url(r'^$', 'index', name='yabackoffice_index'),
    url(r'^radios/(?P<radio_id>\d+)/unmatched/$', 'radio_unmatched_song'),
    url(r'^radios/(?P<radio_id>\d+)/songs/$', 'radio_songs'),
    url(r'^radios/(?P<radio_id>\d+)/remove_songs/$', 'radio_remove_songs'),
    url(r'^radios/(?P<radio_id>\d+)/remove_all_songs/$', 'radio_remove_all_songs'),
    url(r'^radios/(?P<radio_id>\d+)/remove_duplicate_songs/$', 'radio_remove_duplicate_songs'),
    url(r'^radios/(?P<radio_id>\d+)/add_songs/$', 'radio_add_songs'),
    url(r'^radios/(?P<radio_id>\d+)/duplicate/$', 'radio_duplicate'),
    url(r'^radios/(?P<radio_id>\d+)/blacklist/$', 'radio_blacklist'),
    url(r'^radios/(?P<radio_id>\d+)/unblacklist/$', 'radio_unblacklist'),
    url(r'^radios/(?P<radio_id>\d+)/export_stats/$', 'radio_export_stats'),
    url(r'^radios$', 'radios'),
    url(r'^radios/(?P<radio_id>\d+)$', 'radios'),
    url(r'^radios/stats/created/$', 'radios_stats_created'),

    url(r'^songmetadata/top_missing/$', 'songmetadata_top_missing'),
    url(r'^songmetadata/most_popular/$', 'songmetadata_most_popular'),
    url(r'^songmetadata/export_most_popular/$', 'songmetadata_export_most_popular'),

    url(r'^yasound_songs$', 'yasound_songs'),
    url(r'^yasound_songs/find_metadata/$', 'yasound_songs_find_metadata'),
    url(r'^yasound_songs/replace_metadata/$', 'yasound_songs_replace_metadata'),
    url(r'^rejected_songs$', 'rejected_songs'),

    url(r'^invitations/$', 'invitations', {'type': 'all'}),
    url(r'^invitations/pending$', 'invitations', {'type': 'pending'}),
    url(r'^invitations/pending/(?P<invitation_id>\d+)$', 'invitations', {'type': 'pending'}),

    url(r'^invitations/sent/$', 'invitations', {'type': 'sent'}),
    url(r'^invitations/accepted/$', 'invitations', {'type': 'accepted'}),
    url(r'^invitations/save/$', 'invitation_save'),
    url(r'^invitations/(?P<invitation_id>\d+)/generate_message/$', 'invitation_generate_message'),
    url(r'^invitations/(?P<invitation_id>\d+)/send/$', 'invitation_send'),
    url(r'^users$', 'users'),
    url(r'^users/$', 'users'),
    url(r'^users/history/$', 'users_history'),

    url(r'^wall_events$', 'wall_events'),
    url(r'^wall_events/(?P<wall_event_id>\d+)$', 'wall_events'),

    url(r'^keyfigures/', 'keyfigures'),
    url(r'^metrics/$', 'metrics'),
    url(r'^metrics/export/$', 'metrics_export'),
    url(r'^radio_tags/', 'radio_tags'),
    url(r'^past_month_metrics/$', 'past_month_metrics'),
    url(r'^past_month_metrics/export/$', 'past_month_metrics_export'),
    url(r'^past_year_metrics/$', 'past_year_metrics'),
    url(r'^past_year_metrics/export/$', 'past_year_metrics_export'),
    url(r'^metrics/graphs/animators/$', 'metrics_graph_animators'),
    url(r'^metrics/graphs/shares/$', 'metrics_graph_shares'),
    url(r'^metrics/graphs/listen/$', 'metrics_graph_listen'),
    url(r'^metrics/graphs/posts/$', 'metrics_graph_posts'),
    url(r'^metrics/graphs/likes/$', 'metrics_graph_likes'),
    url(r'^light_metrics/', 'light_metrics', name='light_metrics'),


    url(r'^radio_activity_score_factors$', 'radio_activity_score_factors'),
    url(r'^radio_activity_score_factors/(?P<coeff_id>\S+)$', 'radio_activity_score_factors'),

    url(r'^find_musicbrainz_id/$', 'find_musicbrainz_id'),

    url(r'^abuse_notifications$', 'abuse_notifications'),
    url(r'^abuse/delete/$', 'delete_abuse_notification'),
    url(r'^abuse/ignore/$', 'ignore_abuse_notification'),


    url(r'^premium/unique_promocodes/$', 'premium_unique_promocodes'),
    url(r'^premium/non_unique_promocodes/$', 'premium_non_unique_promocodes'),
    url(r'^premium/promocodes/(?P<promocode_id>\d+)/$', 'premium_promocodes'),
    url(r'^premium/promocodes/$', 'premium_promocodes'),

    url(r'^geoperm/countries/$', 'geoperm_countries'),
    url(r'^geoperm/countries/(?P<country_id>\d+)/$', 'geoperm_countries'),
    url(r'^geoperm/countries/(?P<country_id>\d+)/features/$', 'geoperm_countries_features'),
    url(r'^geoperm/countries/(?P<country_id>\d+)/features/(?P<geofeature_id>\d+)/$', 'geoperm_countries_features'),

)