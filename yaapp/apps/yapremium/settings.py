from django.utils.translation import ugettext_lazy as _

ACTION_CREATE_ACCOUNT = 0
ACTION_WATCH_TUTORIAL = 1
ACTION_ADD_FACEBOOK_ACCOUNT = 2
ACTION_ADD_TWITTER_ACCOUNT = 3
ACTION_INVITE_FRIENDS = 4

ACTION_CHOICES = (
    (ACTION_CREATE_ACCOUNT, _('Create account')),
    (ACTION_WATCH_TUTORIAL, _('Watch tutorial')),
    (ACTION_ADD_FACEBOOK_ACCOUNT, _('Add facebook account')),
    (ACTION_ADD_TWITTER_ACCOUNT, _('Add twitter account')),
    (ACTION_INVITE_FRIENDS, _('Invite friends')),
)


SERVICE_HD = 0
SERVICE_SELECTION = 1
SERVICE_CHOICES = (
    (SERVICE_HD, _('HD')),
    (SERVICE_SELECTION, _('Selection')),
)
