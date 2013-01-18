from django.db import models
from django.utils.translation import ugettext_lazy as _
from transmeta import TransMeta
import markdown


class FaqEntryManager(models.Manager):
    def get_entries(self):
        return self.all().order_by('order')


class FaqEntry(models.Model):
    """Faq Entry"""

    __metaclass__ = TransMeta

    objects = FaqEntryManager()
    title = models.CharField(_('title'), max_length=120)
    content = models.TextField(_('content'))
    created = models.DateTimeField(_('created at'), auto_now_add=True)
    updated = models.DateTimeField(_('created at'), auto_now=True)
    order = models.IntegerField(_('order'), default=0)

    class Meta:
        verbose_name = _('faq entry')
        verbose_name_plural = _('faq entries')
        ordering = ['order']
        translate = ('title', 'content',)

    def as_dict(self):
        data = {
            'id': self.id,
            'title': self.name,
            'created': self.created,
            'updated': self.updated,
            'content': self.get_content(),
        }
        return data

    def get_content(self):
        return markdown.markdown(self.content, extensions=['extra', 'codehilite'])
