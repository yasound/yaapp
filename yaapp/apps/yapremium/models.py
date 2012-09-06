from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from datetime import *
from dateutil.relativedelta import *
from sorl.thumbnail import get_thumbnail, delete
import settings as yapremium_settings
from yabase.models import Radio


class Service(models.Model):
    created = models.DateTimeField(_('created'), auto_now_add=True)
    updated = models.DateTimeField(_('updated'), auto_now=True)
    stype = models.IntegerField(_('service'), choices=yapremium_settings.SERVICE_CHOICES, unique=True)

    class Meta:
        verbose_name = _('service')

    def __unicode__(self):
        return u'%s' % (self.get_stype_display())

    def activate(self, user):
        profile = user.get_profile()
        stype = self.stype
        if stype == yapremium_settings.SERVICE_HD:
            profile.permissions.hd = True
        if stype == yapremium_settings.SERVICE_SELECTION:
            profile.permissions.selection = True
        profile.save()

    def disable(self, user):
        profile = user.get_profile()
        stype = self.stype
        if stype == yapremium_settings.SERVICE_HD:
            profile.permissions.hd = False
        if stype == yapremium_settings.SERVICE_SELECTION:
            profile.permissions.selection = False
        profile.save()


class SubscriptionManager(models.Manager):
    def available_subscriptions(self):
        return self.filter(enabled=True)


class Subscription(models.Model):
    objects = SubscriptionManager()
    created = models.DateTimeField(_('created'), auto_now_add=True)
    updated = models.DateTimeField(_('updated'), auto_now=True)
    name = models.CharField(_('name'), max_length=255, blank=True)
    sku = models.CharField(_('sku'), max_length=255, blank=True)
    description = models.TextField(_('description'), blank=True)
    duration = models.IntegerField(_('duration'), default=1)
    enabled = models.BooleanField(_('enabled'), default=False)
    order = models.IntegerField(_('order'), default=0)
    highlighted = models.BooleanField(_('highlighted'), default=False)
    services = models.ManyToManyField(Service, verbose_name=_('services'))

    def as_dict(self, request_user):
        data = {
            'id': self.id,
            'sku': self.sku,
            'duration': self.duration,
            'enabled': self.enabled,
            'highlighted': self.highlighted,
        }
        return data

    def __unicode__(self):
        return u'%s' % (self.name)

    def calculate_expiration_date(self, today=None):
        if not today:
            today = date.today()
        return today + relativedelta(months=+self.duration)

    class Meta:
        verbose_name = _('subscription')


class UserSubscription(models.Model):
    created = models.DateTimeField(_('created'), auto_now_add=True)
    updated = models.DateTimeField(_('updated'), auto_now=True)
    user = models.ForeignKey(User, verbose_name=_('user'))
    subscription = models.ForeignKey(Subscription, verbose_name=_('subscription'))
    expiration_date = models.DateTimeField(_('expiration date'), null=True, blank=True)

    class Meta:
        verbose_name = _('user subscription')
        verbose_name_plural = _('user subscriptions')

    def save(self, *args, **kwargs):
        self.expiration_date = self.subscription.calculate_expiration_date()
        super(UserSubscription, self).save(*args, **kwargs)

        for service in self.subscription.services.all():
            us, _created = UserService.objects.get_or_create(service=service, user=self.user)
            if not us.active:
                us.expiration_date = self.subscription.calculate_expiration_date()
            else:
                us.expiration_date = self.subscription.calculate_expiration_date(us.expiration_date)
            us.active = True
            us.save()

    def __unicode__(self):
        return u'%s - %s' % (unicode(self.user), unicode(self.subscription))


class UserService(models.Model):
    created = models.DateTimeField(_('created'), auto_now_add=True)
    updated = models.DateTimeField(_('updated'), auto_now=True)
    user = models.ForeignKey(User, verbose_name=_('user'))
    service = models.ForeignKey(Service, verbose_name=_('service'))
    active = models.BooleanField('Active', default=True)
    expiration_date = models.DateTimeField(_('expiration date'), null=True, blank=True)

    class Meta:
        verbose_name = _('user service')
        verbose_name_plural = _('user services')
        unique_together = ('user', 'service')

    def __unicode__(self):
        return u'%s - %s' % (unicode(self.user), unicode(self.service))

    def save(self, *args, **kwargs):
        if self.active:
            self.service.activate(self.user)
        else:
            self.service.disable(self.user)
        super(UserService, self).save(*args, **kwargs)

    def as_dict(self):
        data = {
            'id': self.id,
            'service': self.service.get_stype_display(),
            'active': self.active,
            'expiration_date': self.expiration_date,
        }
        return data


class Gift(models.Model):
    created = models.DateTimeField(_('created'), auto_now_add=True)
    updated = models.DateTimeField(_('updated'), auto_now=True)
    enabled = models.BooleanField(_('enabled'), default=False)

    name = models.CharField(_('name'), max_length=255, blank=True)
    description = models.TextField(_('description'), blank=True)

    action = models.IntegerField(_('action'), choices=yapremium_settings.ACTION_CHOICES)
    action_url_ios = models.TextField(_('iOS action url'), blank=True)

    service = models.ForeignKey(Service, verbose_name=_('service'))
    duration = models.IntegerField(_('duration'), default=1)
    max_per_user = models.IntegerField(_('max per user'), default=1)

    picture_todo = models.ImageField(upload_to=settings.PICTURE_FOLDER, null=True, blank=True)
    picture_done = models.ImageField(upload_to=settings.PICTURE_FOLDER, null=True, blank=True)

    @property
    def picture_todo_url(self):
        if self.picture_todo:
            try:
                return get_thumbnail(self.picture_todo, '210x210', format='PNG', crop='center').url
            except:
                pass
        return settings.GIFT_DEFAULT_IMAGE_TODO

    @property
    def picture_done_url(self):
        if self.picture_done:
            try:
                return get_thumbnail(self.picture_done, '210x210', format='PNG', crop='center').url
            except:
                pass
        return settings.GIFT_DEFAULT_IMAGE_DONE

    def as_dict(self, user):
        count = 0
        last_achievement_date = None
        if user is not None and user.is_authenticated():
            achievements = Achievement.objects.filter(user=user).order_by('-achievement_date')
            count = achievements.count()
            if count > 0:
                last_achievement_date = achievements[0].achievement_date

        enabled = True
        if not self.enabled:
            enabled = False
        elif count == self.max_per_user:
            enabled = False

        if count > 0:
            picture_url = self.picture_todo_url
        else:
            picture_url = self.picture_done_url

        data = {
            'id': self.id,
            'enabled': enabled,
            'name': self.name,
            'description': self.description,
            'max': self.max_per_user,
            'count': count,
            'last_achievement_date': last_achievement_date,
            'picture_url': picture_url
        }
        return data

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('gift')


class Achievement(models.Model):
    created = models.DateTimeField(_('created'), auto_now_add=True)
    updated = models.DateTimeField(_('updated'), auto_now=True)
    user = models.ForeignKey(User, verbose_name=_('user'))
    gift = models.ForeignKey(Gift, verbose_name=_('gift'))
    achievement_date = models.DateTimeField(_('achievement date'))

    def __unicode__(self):
        return u'%s-%s-%s' % (self.user, self.rule, self.achievement_date)

    class Meta:
        verbose_name = _('achievement')
