from django.utils.translation import ugettext_lazy as _

MOOD_NEUTRAL = 'N'
MOOD_LIKE = 'L'
MOOD_DISLIKE = 'D'

MOOD_CHOICES = (
                (MOOD_LIKE, _('Like')),
                (MOOD_DISLIKE, _('Dislike')),
                (MOOD_NEUTRAL, _('Neutral'))
                )

EVENT_JOINED = 'J'
EVENT_LEFT = 'L'
EVENT_MESSAGE = 'M'
EVENT_SONG = 'S'

EVENT_TYPE_CHOICES = (
                        (EVENT_JOINED, _('Joined')),
                        (EVENT_LEFT, _('Left')),
                        (EVENT_MESSAGE, _('Message')),
                        (EVENT_SONG, _('Song')),
                    )