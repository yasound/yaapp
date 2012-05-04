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
    url(r'^radios$', 'radios'),
    url(r'^radios/(?P<radio_id>\d+)$', 'radios'),
    url(r'^radios/stats/created/$', 'radios_stats_created'),

    url(r'^songmetadata/top_missing/$', 'songmetadata_top_missing'),

    url(r'^yasound_songs$', 'yasound_songs'),
    
    url(r'^invitations/$', 'invitations', {'type': 'all'}),
    url(r'^invitations/pending$', 'invitations', {'type': 'pending'}),
    url(r'^invitations/pending/(?P<invitation_id>\d+)$', 'invitations', {'type': 'pending'}),

    url(r'^invitations/sent/$', 'invitations', {'type': 'sent'}),
    url(r'^invitations/accepted/$', 'invitations', {'type': 'accepted'}),
    url(r'^invitations/save/$', 'invitation_save'),
    url(r'^invitations/(?P<invitation_id>\d+)/generate_message/$', 'invitation_generate_message'),
    url(r'^invitations/(?P<invitation_id>\d+)/send/$', 'invitation_send'),
    url(r'^users', 'users'),

    url(r'^keyfigures/', 'keyfigures'),
    url(r'^metrics/', 'metrics'),
    url(r'^light_metrics/', 'light_metrics', name='light_metrics'),
)