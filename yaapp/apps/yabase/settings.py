from django.utils.translation import ugettext_lazy as _

# Radio origin
RADIO_ORIGIN_YASOUND    = 0
RADIO_ORIGIN_RADIOWAYS  = 1
RADIO_ORIGIN_EXTERNAL   = 2
RADIO_ORIGIN_KFM        = 3

RADIO_ORIGIN_CHOICES = (
    (RADIO_ORIGIN_YASOUND, _('Yasound')),
    (RADIO_ORIGIN_RADIOWAYS, _('Radioways')),
    (RADIO_ORIGIN_EXTERNAL, _('External')),
    (RADIO_ORIGIN_KFM, _('k-fm')),
)

# Radio styles
RADIO_STYLE_ALL         = 'style_all'
RADIO_STYLE_CLASSICAL   = 'style_classique'
RADIO_STYLE_BLUES       = 'style_blues'
RADIO_STYLE_ALTERNATIVE = 'style_alternative'
RADIO_STYLE_ELECTRO     = 'style_electro'
RADIO_STYLE_FRENCH      = 'style_chanson_francaise'
RADIO_STYLE_JAZZ        = 'style_jazz'
RADIO_STYLE_POP         = 'style_pop'
RADIO_STYLE_REGGAE      = 'style_reggae'
RADIO_STYLE_ROCK        = 'style_rock'
RADIO_STYLE_METAL       = 'style_metal'
RADIO_STYLE_HIPHOP      = 'style_hiphop'
RADIO_STYLE_RNBSOUL     = 'style_rnbsoul'
RADIO_STYLE_WORLD       = 'style_world'
RADIO_STYLE_MISC        = 'style_misc'

RADIO_STYLE_NONE        = ''

RADIO_STYLE_CHOICES = (
    (RADIO_STYLE_CLASSICAL, _('Classical')),
    (RADIO_STYLE_BLUES, _('Blues')),
    (RADIO_STYLE_ALTERNATIVE, _('Alternative')),
    (RADIO_STYLE_ELECTRO, _('Electro')),
    (RADIO_STYLE_FRENCH, _('French Music')),
    (RADIO_STYLE_JAZZ, _('Jazz')),
    (RADIO_STYLE_POP, _('Pop')),
    (RADIO_STYLE_REGGAE, _('Reggae')),
    (RADIO_STYLE_ROCK, _('Rock')),
    (RADIO_STYLE_METAL, _('Metal')),
    (RADIO_STYLE_HIPHOP, _('Hip hop')),
    (RADIO_STYLE_RNBSOUL, _('RnB / Soul')),
    (RADIO_STYLE_WORLD, _('World')),
    (RADIO_STYLE_MISC, _('Miscellaneous')),
    (RADIO_STYLE_ALL, _('All genres')),
)

RADIO_STYLE_CHOICES_FORM = (
    (RADIO_STYLE_NONE, _('Genre')),
) + RADIO_STYLE_CHOICES

# Mood
MOOD_NEUTRAL = 'N'
MOOD_LIKE = 'L'
MOOD_DISLIKE = 'D'

MOOD_CHOICES = (
                (MOOD_LIKE, _('Like')),
                (MOOD_DISLIKE, _('Dislike')),
                (MOOD_NEUTRAL, _('Neutral'))
                )

EVENT_MESSAGE = 'M'
EVENT_SONG = 'S'
EVENT_LIKE = 'L'

EVENT_TYPE_CHOICES = (
                        (EVENT_MESSAGE, _('Message')),
                        (EVENT_SONG, _('Song')),
                        (EVENT_LIKE, _('Like')),
                    )

FUZZY_COMMON_WORDS = ("the", "for", "a", "of", 'and')

YASOUND_FAVORITES_PLAYLIST_NAME = '#yasound_songs_from_other_radios'
YASOUND_FAVORITES_PLAYLIST_SOURCE_BASENAME = '#yasound_songs_from_other_radios_source'

UPLOAD_KEY='weeriwjwsdiwew9ei9nksxsdwxj,.29x2jdnjweapnfnhshdf'

DEFAULT_FILENAME='file'

TOP_RADIOS_LIMIT = 25
MOST_ACTIVE_RADIOS_LIMIT = 18

RADIO_RECOMMENDATION_COMPUTE_COUNT = 300
RADIO_SELECTION_VIEW_COUNT = 4
RADIO_SELECTION_VIEW_COUNT_IPHONE = 2

IPHONE_DEFAULT_APPLICATION_IDENTIFIER = 'com.yasound.yasound'
IPHONE_TECH_TOUR_APPLICATION_IDENTIFIER = 'com.yasound.techtour'

TECH_TOUR_GROUP_NAME = 'techtour'


# feature stuff
FEATURED_SELECTION = 'S'
FEATURED_HOMEPAGE  = 'H'
FEATURED_CHOICES = (
    (FEATURED_SELECTION, _('Selection')),
    (FEATURED_HOMEPAGE, _('Homepage')),
)


ANIMATOR_TYPE_CREATE_RADIO      = 'create_radio'
ANIMATOR_TYPE_UPLOAD_PLAYLIST   = 'upload_playlist'
ANIMATOR_TYPE_UPLOAD_SONG       = 'upload_song'
ANIMATOR_TYPE_ADD_SONG          = 'add_song'
ANIMATOR_TYPE_REJECT_SONG       = 'reject_song'
ANIMATOR_TYPE_DELETE_SONG       = 'delete_song'
ANIMATOR_TYPE_IMPORT_ITUNES     = 'import_itunes'
