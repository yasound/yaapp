from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
import settings as yapremium_settings


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

    def as_dict(self, request_user):
        data = {
            'id': self.id,
            'sku': self.sku,
            'duration': self.duration,
            'enabled': self.enabled,
            'current': False
        }
        if request_user:
            uss = UserSubscription.objects.filter(user=request_user, active=True)[:1]
            if uss.count() > 0:
                us = uss[0]
                if us.subscription.id == self.id:
                    data['current'] = True
                    data['expiration_date'] = us.expiration_date
                elif us.subscription.order > self.order:
                    data['enabled'] = False
        return data

    def __unicode__(self):
        return u'%s' % (self.name)

    class Meta:
        verbose_name = _('subscription')


class UserSubscription(models.Model):
    created = models.DateTimeField(_('created'), auto_now_add=True)
    updated = models.DateTimeField(_('updated'), auto_now=True)
    user = models.ForeignKey(User, verbose_name=_('user'))
    subscription = models.ForeignKey(Subscription, verbose_name=_('subscription'))
    achievement = models.ForeignKey('Achievement', verbose_name=_('achievement'), null=True, blank=True)
    active = models.BooleanField('Active', default=True)
    expiration_date = models.DateTimeField(_('expiration date'))

    def __unicode__(self):
        return u'%s - %s' % (unicode(self.user), unicode(self.subscription))

    class Meta:
        verbose_name = _('user subscription')
        verbose_name_plural = _('user subscriptions')


class GiftRule(models.Model):
    created = models.DateTimeField(_('created'), auto_now_add=True)
    updated = models.DateTimeField(_('updated'), auto_now=True)
    action = models.IntegerField(_('action'), choices=yapremium_settings.ACTION_CHOICES)
    gift = models.ForeignKey(Subscription, verbose_name=_('subscription'))
    unit = models.IntegerField(_('unit'), default=1)
    max_per_user = models.IntegerField(_('max per user'), default=1)
    enabled = models.BooleanField(_('enabled'), default=False)

    def __unicode__(self):
        return u'%s' % (self.get_action_display)

    class Meta:
        verbose_name = _('gift rule')
        verbose_name_plural = _('gift rules')


class Achievement(models.Model):
    created = models.DateTimeField(_('created'), auto_now_add=True)
    updated = models.DateTimeField(_('updated'), auto_now=True)
    user = models.ForeignKey(User, verbose_name=_('user'))
    rule = models.ForeignKey(GiftRule, verbose_name=_('rule'))
    achievement_date = models.DateTimeField(_('achievement date'))

    def __unicode__(self):
        return u'%s-%s-%s' % (self.user, self.rule, self.achievement_date)

    class Meta:
        verbose_name = _('achievement')
