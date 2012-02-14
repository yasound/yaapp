from django.utils.translation import ugettext_lazy as _

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

EVENT_TYPE_CHOICES = (
                        (EVENT_MESSAGE, _('Message')),
                        (EVENT_SONG, _('Song')),
                    )

FUZZY_COMMON_WORDS = ("the", "for", "a", "of", 'and')

YASOUND_FAVORITES_PLAYLIST_NAME = '#yasound_songs_from_other_radios'
YASOUND_FAVORITES_PLAYLIST_SOURCE_BASENAME = '#yasound_songs_from_other_radios_source'