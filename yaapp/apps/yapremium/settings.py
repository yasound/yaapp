from django.utils.translation import ugettext_lazy as _

ACTION_CREATE_ACCOUNT           = 0
ACTION_WATCH_TUTORIAL           = 1
ACTION_ADD_FACEBOOK_ACCOUNT     = 2
ACTION_ADD_TWITTER_ACCOUNT      = 3
ACTION_INVITE_FRIENDS           = 4
ACTION_ADD_EMAIL_ACCOUNT        = 5
ACTION_FOLLOW_YASOUND_TWITTER   = 6
ACTION_REGISTER_NEWSLETTER      = 7
ACTION_CREATE_RADIO             = 8
ACTION_UPDATE_PROGRAMMING       = 9
ACTION_FILL_IN_PROFILE          = 10
ACTION_VIEW_NOTIFICATIONS       = 11
ACTION_VIEW_STATS               = 12

ACTION_CHOICES = (
    (ACTION_CREATE_ACCOUNT,         _('Create account')),
    (ACTION_WATCH_TUTORIAL,         _('Watch tutorial')),
    (ACTION_ADD_FACEBOOK_ACCOUNT,   _('Add facebook account')),
    (ACTION_ADD_TWITTER_ACCOUNT,    _('Add twitter account')),
    (ACTION_INVITE_FRIENDS,         _('Invite friends')),
    (ACTION_ADD_EMAIL_ACCOUNT,      _('Add email account')),
    (ACTION_FOLLOW_YASOUND_TWITTER, _('Follow Yasound on Twitter')),
    (ACTION_REGISTER_NEWSLETTER,    _('Register newsletter')),
    (ACTION_CREATE_RADIO,           _('Create radio')),
    (ACTION_UPDATE_PROGRAMMING,     _('Update programming')),
    (ACTION_FILL_IN_PROFILE,        _('Fill in profile')),
    (ACTION_VIEW_NOTIFICATIONS,     _('View notifications')),
    (ACTION_VIEW_STATS,             _('View stats')),
)

SERVICE_HD = 0
SERVICE_SELECTION = 1
SERVICE_CHOICES = (
    (SERVICE_HD, _('HD')),
    (SERVICE_SELECTION, _('Selection')),
)

DURATION_DAY = 0
DURATION_WEEK = 1
DURATION_MONTH = 2

DURATION_UNIT_CHOICES = (
    (DURATION_DAY, _('Day')),
    (DURATION_WEEK, _('Week')),
    (DURATION_MONTH, _('Month')),
)
