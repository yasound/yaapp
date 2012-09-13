from django.utils.translation import ugettext_lazy as _

FEATURE_LOGIN = 0
FEATURE_CREATE_RADIO = 1

FEATURE_CHOICES = (
    (FEATURE_LOGIN, _('Login')),
    (FEATURE_CREATE_RADIO, _('Create radio')),
)
