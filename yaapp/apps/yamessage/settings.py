from django.utils.translation import ugettext_lazy as _

TYPE_NOTIF_FRIEND_IN_RADIO      = 'type_notif_friend_in_radio'
TYPE_NOTIF_USER_IN_RADIO        = 'type_notif_user_in_radio'
TYPE_NOTIF_FRIEND_ONLINE        = 'type_notif_friend_online'
TYPE_NOTIF_MESSAGE_IN_WALL      = 'type_notif_message_in_wall'
TYPE_NOTIF_SONG_LIKED           = 'type_notif_song_liked'
TYPE_NOTIF_RADIO_IN_FAVORITES   = 'type_notif_radio_in_favorites'
TYPE_NOTIF_RADIO_SHARED         = 'type_notif_radio_shared'
TYPE_NOTIF_FRIEND_CREATED_RADIO = 'type_notif_friend_created_radio'
TYPE_NOTIF_MESSAGE_FROM_YASOUND = 'type_notif_message_from_yasound'
TYPE_NOTIF_MESSAGE_FROM_USER    = 'type_notif_message_from_user'

APNS_LOC_KEY_FRIEND_IN_RADIO      = 'APNs_FIR'
APNS_LOC_KEY_USER_IN_RADIO        = 'APNs_UIR'
APNS_LOC_KEY_FRIEND_ONLINE        = 'APNs_FOn'
APNS_LOC_KEY_MESSAGE_IN_WALL      = 'APNs_Msg'
APNS_LOC_KEY_SONG_LIKED           = 'APNs_Sng'
APNS_LOC_KEY_RADIO_IN_FAVORITES   = 'APNs_RIF'
APNS_LOC_KEY_RADIO_SHARED         = 'APNs_RSh'
APNS_LOC_KEY_FRIEND_CREATED_RADIO = 'APNs_FCR'
APNS_LOC_KEY_MESSAGE_FROM_YASOUND = 'APNs_YAS'
APNS_LOC_KEY_MESSAGE_FROM_USER    = 'APNs_USR'


TEXT_NOTIF_FRIEND_IN_RADIO      = _("%(user_name)s is listening to your radio \"%(radio_name)s\"")
TEXT_NOTIF_USER_IN_RADIO        = _("%(user_name)s is listening to your radio \"%(radio_name)s\"")
TEXT_NOTIF_FRIEND_ONLINE        = _("%(user_name)s is online on Yasound")
TEXT_NOTIF_MESSAGE_IN_WALL      = _("%(user_name)s posted a message on your radio \"%(radio_name)s\"")
TEXT_NOTIF_SONG_LIKED           = _("%(user_name)s liked '%(song_name)s' on radio \"%(radio_name)s\"")
TEXT_NOTIF_RADIO_IN_FAVORITES   = _("%(user_name)s added \"%(radio_name)s\" as a favorite")
TEXT_NOTIF_RADIO_SHARED         = _("%(user_name)s shared your radio \"%(radio_name)s\"")
TEXT_NOTIF_FRIEND_CREATED_RADIO = _("%(user_name)s created a radio: \"%(radio_name)s\"")
TEXT_NOTIF_MESSAGE_FROM_YASOUND = _("you have a message from Yasound")
TEXT_NOTIF_MESSAGE_FROM_USER    = _("%s")

HTML_NOTIF_FRIEND_IN_RADIO      = _("<a class='profile' data-username='%(user_username)s' href='/app/profile/%(user_username)s/'>%(user_name)s</a> is listening to your radio")
HTML_NOTIF_USER_IN_RADIO        = _("<a class='profile' data-username='%(user_username)s' href='/app/profile/%(user_username)s/'>%(user_name)s</a> is listening to your radio")
HTML_NOTIF_FRIEND_ONLINE        = _("<a class='profile' data-username='%(user_username)s' href='/app/profile/%(user_username)s/'>%(user_name)s</a> is online on Yasound")
HTML_NOTIF_MESSAGE_IN_WALL      = _("<a class='profile' data-username='%(user_username)s' href='/app/profile/%(user_username)s/'>%(user_name)s</a> posted a message on your wall")
HTML_NOTIF_SONG_LIKED           = _("<a class='profile' data-username='%(user_username)s' href='/app/profile/%(user_username)s/'>%(user_name)s</a> liked '%(song_name)s' on your radio")
HTML_NOTIF_RADIO_IN_FAVORITES   = _("<a class='profile' data-username='%(user_username)s' href='/app/profile/%(user_username)s/'>%(user_name)s</a> added your radio as a favorite")
HTML_NOTIF_RADIO_SHARED         = _("<a class='profile' data-username='%(user_username)s' href='/app/profile/%(user_username)s/'>%(user_name)s</a> shared your radio")
HTML_NOTIF_FRIEND_CREATED_RADIO = _("<a class='profile' data-username='%(user_username)s' href='/app/profile/%(user_username)s/'>%(user_name)s</a> created his radio")
HTML_NOTIF_MESSAGE_FROM_YASOUND = _("you have a message from Yasound")
HTML_NOTIF_MESSAGE_FROM_USER    = _("%s")

YASOUND_NOTIF_PARAMS_ATTRIBUTE_NAME = 'yasound_notif_params'

NOTIF_INFOS = {
               TYPE_NOTIF_FRIEND_IN_RADIO: {
                                            'text': TEXT_NOTIF_FRIEND_IN_RADIO,
                                            'html': HTML_NOTIF_FRIEND_IN_RADIO,
                                            'loc_key': APNS_LOC_KEY_FRIEND_IN_RADIO
                                            },
               TYPE_NOTIF_USER_IN_RADIO: {
                                            'text': TEXT_NOTIF_USER_IN_RADIO,
                                            'html': HTML_NOTIF_USER_IN_RADIO,
                                            'loc_key': APNS_LOC_KEY_USER_IN_RADIO
                                            },
               TYPE_NOTIF_FRIEND_ONLINE: {
                                            'text': TEXT_NOTIF_FRIEND_ONLINE,
                                            'html': HTML_NOTIF_FRIEND_ONLINE,
                                            'loc_key': APNS_LOC_KEY_FRIEND_ONLINE
                                            },
               TYPE_NOTIF_MESSAGE_IN_WALL: {
                                            'text': TEXT_NOTIF_MESSAGE_IN_WALL,
                                            'html': HTML_NOTIF_MESSAGE_IN_WALL,
                                            'loc_key': APNS_LOC_KEY_MESSAGE_IN_WALL
                                            },
               TYPE_NOTIF_SONG_LIKED: {
                                            'text': TEXT_NOTIF_SONG_LIKED,
                                            'html': HTML_NOTIF_SONG_LIKED,
                                            'loc_key': APNS_LOC_KEY_SONG_LIKED
                                            },
               TYPE_NOTIF_RADIO_IN_FAVORITES: {
                                            'text': TEXT_NOTIF_RADIO_IN_FAVORITES,
                                            'html': HTML_NOTIF_RADIO_IN_FAVORITES,
                                            'loc_key': APNS_LOC_KEY_RADIO_IN_FAVORITES
                                            },
               TYPE_NOTIF_RADIO_SHARED: {
                                            'text': TEXT_NOTIF_RADIO_SHARED,
                                            'html': HTML_NOTIF_RADIO_SHARED,
                                            'loc_key': APNS_LOC_KEY_RADIO_SHARED
                                            },
               TYPE_NOTIF_FRIEND_CREATED_RADIO: {
                                            'text': TEXT_NOTIF_FRIEND_CREATED_RADIO,
                                            'html': HTML_NOTIF_FRIEND_CREATED_RADIO,
                                            'loc_key': APNS_LOC_KEY_FRIEND_CREATED_RADIO
                                            },
               TYPE_NOTIF_MESSAGE_FROM_YASOUND: {
                                            'text': TEXT_NOTIF_MESSAGE_FROM_YASOUND,
                                            'html': HTML_NOTIF_MESSAGE_FROM_YASOUND,
                                            'loc_key': APNS_LOC_KEY_MESSAGE_FROM_YASOUND
                                            },
               TYPE_NOTIF_MESSAGE_FROM_USER: {
                                            'text': TEXT_NOTIF_MESSAGE_FROM_USER,
                                            'html': HTML_NOTIF_MESSAGE_FROM_USER,
                                            'loc_key': APNS_LOC_KEY_MESSAGE_FROM_USER
                                            },
               }
