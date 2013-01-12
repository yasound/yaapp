from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from transmeta import TransMeta
from datetime import datetime
from taggit.managers import TaggableManager


class BlogPostManager(models.Manager):
    def get_posts(self):
        now = datetime.now()
        return self.filter(state=BlogPost.STATE_PUBLISHED, publish_date__lte=now).order_by('-sticky', '-publish_date')


class BlogPost(models.Model):
    """Blog post"""

    __metaclass__ = TransMeta

    objects = BlogPostManager()
    name = models.CharField(_('name'), max_length=80, unique=True)
    slug = models.SlugField(_('slug'))
    creator = models.ForeignKey(User)
    created = models.DateTimeField(_('created at'), auto_now_add=True)
    updated = models.DateTimeField(_('created at'), auto_now=True)
    publish_date = models.DateTimeField(_('publish date'), blank=True, null=True)
    teaser = models.TextField(_('teaser'), blank=True)
    description = models.TextField(_('description'))
    sticky = models.BooleanField(_('sticky'), default=False)
    tags = TaggableManager(_('tags'), blank=True)

    STATE_DRAFT = 1
    STATE_PUBLISHED = 2
    STATE_DELETED = 3

    STATE_CHOICES = (
        (STATE_DRAFT, _('Draft')),
        (STATE_PUBLISHED, _('Published')),
        (STATE_DELETED, _('Deleted')),
    )
    state = models.IntegerField(_('state'), choices=STATE_CHOICES, default=STATE_DRAFT)

    tags = TaggableManager(blank=True)

    class Meta:
        verbose_name = _('blog post')
        verbose_name_plural = _('blog posts')
        ordering = ['-sticky', '-publish_date', 'slug']
        translate = ('name', 'teaser', 'description')

    def as_dict(self):
        data = {
            'id': self.id,
            'creator': self.creator.get_profile().as_dict(),
            'name': self.name,
            'slug': self.slug,
            'created': self.created,
            'updated': self.updated,
            'teaser': self.get_teaser(),
            'description': self.description,
            'sticky': self.sticky,
            'tags': self.tags_to_string(),
        }
        return data

    def get_teaser(self):
        if self.teaser != '':
            return self.teaser
        return self.description

    def tags_to_string(self):
        first = True
        tags_str = ''
        for tag in self.tags.all():
            t = tag.name
            if first:
                tags_str += t
                first = False
            else:
                tags_str += ','
                tags_str += t
        return tags_str

    @property
    def comp_date(self):
        return self.publish_date

    @models.permalink
    def get_absolute_url(self):
        return ('blog_post', None, {
            'year': self.publish_date.year,
            'month': "%02d" % self.publish_date.month,
            'day': "%02d" % self.publish_date.day,
            'slug': self.slug
        })
