from django.utils.translation import ugettext_lazy as _
from django.db import models
import settings as yageoperm_settings

class Country(models.Model):
    created = models.DateTimeField(_('created'), auto_now_add=True)
    updated = models.DateTimeField(_('updated'), auto_now=True)
    code = models.CharField(_('code'), max_length=4, unique=True)
    name = models.CharField(_('name'), max_length=200, unique=True)

    class Meta:
        verbose_name = _('country')

class GeoFeature(models.Model):
    created = models.DateTimeField(_('created'), auto_now_add=True)
    updated = models.DateTimeField(_('updated'), auto_now=True)
    country = models.ForeignKey(Country, verbose_name=_('country'))
    feature = models.IntegerField(_('feature'), choices=yageoperm_settings.FEATURE_CHOICES, default=yageoperm_settings.FEATURE_LOGIN)

    @property
    def feature_display(self):
        return self.get_feature_display()

    class Meta:
        verbose_name = _('geo feature')
        unique_together = ('country', 'feature')
