from django.utils.translation import ugettext_lazy as _

ACTION_WATCH_TUTORIAL = 0

ACTION_CHOICES = (
    (ACTION_WATCH_TUTORIAL, _('Watch tutorial')),
)


SERVICE_HD = 0
SERVICE_SELECTION = 1
SERVICE_CHOICES = (
    (SERVICE_HD, _('HD')),
    (SERVICE_SELECTION, _('Selection')),
)
