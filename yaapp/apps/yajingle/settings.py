from django.utils.translation import ugettext_lazy as _

JINGLE_TYPE_PRIVATE = 0
JINGLE_TYPE_PUBLIC = 1
JINGLE_TYPE_CHOICES = (
    (JINGLE_TYPE_PRIVATE, _('Private')),
    (JINGLE_TYPE_PUBLIC, _('Public')),
)
