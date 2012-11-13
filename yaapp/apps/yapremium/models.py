from django.db import models
from django.db.models import signals
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.auth import signals as auth_signals
from datetime import *
from dateutil.relativedelta import *
from sorl.thumbnail import get_thumbnail
import settings as yapremium_settings
from yacore.http import absolute_url
from account.models import UserProfile, InvitationsManager
from transmeta import TransMeta
from django.core.urlresolvers import reverse
import utils as yapremium_utils

import account.signals as account_signals
from yabase import signals as yabase_signals
from yamessage import signals as yamessage_signals
from yabase.models import Radio
from task import async_win_gift, async_check_for_invitation
from django.db import transaction

import logging
logger = logging.getLogger("yaapp.yapremium")

class Service(models.Model):
    """
    A service which can be activated or disabled
    """
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
    """
    A subscription can be purchased by a user and is related to one ore more services
    """
    __metaclass__ = TransMeta

    objects = SubscriptionManager()
    created = models.DateTimeField(_('created'), auto_now_add=True)
    updated = models.DateTimeField(_('updated'), auto_now=True)
    name = models.CharField(_('name'), max_length=255, blank=True)
    sku = models.CharField(_('sku'), max_length=255, blank=True)
    description = models.TextField(_('description'), blank=True)
    duration = models.IntegerField(_('duration'), default=1)
    duration_unit = models.IntegerField(_('duration unit'), choices=yapremium_settings.DURATION_UNIT_CHOICES, default=yapremium_settings.DURATION_MONTH)
    enabled = models.BooleanField(_('enabled'), default=False)
    order = models.IntegerField(_('order'), default=0)
    highlighted = models.BooleanField(_('highlighted'), default=False)
    services = models.ManyToManyField(Service, verbose_name=_('services'))

    def as_dict(self, request_user):
        data = {
            'id': self.id,
            'sku': self.sku,
            'duration': self.duration,
            'duration_unit': self.duration_unit,
            'enabled': self.enabled,
            'highlighted': self.highlighted,
        }
        return data

    def __unicode__(self):
        return u'%s' % (self.name)

    class Meta:
        verbose_name = _('subscription')
        translate = ('name', 'description', 'sku')


class UserSubscription(models.Model):
    """
    Item bought by a user
    """
    created = models.DateTimeField(_('created'), auto_now_add=True)
    updated = models.DateTimeField(_('updated'), auto_now=True)
    user = models.ForeignKey(User, verbose_name=_('user'))
    subscription = models.ForeignKey(Subscription, verbose_name=_('subscription'))
    expiration_date = models.DateTimeField(_('expiration date'), null=True, blank=True)

    class Meta:
        verbose_name = _('user subscription')
        verbose_name_plural = _('user subscriptions')

    def save(self, *args, **kwargs):
        self.expiration_date = yapremium_utils.calculate_expiration_date(duration=self.subscription.duration, duration_unit=self.subscription.duration_unit)
        super(UserSubscription, self).save(*args, **kwargs)

        for service in self.subscription.services.all():
            us, _created = UserService.objects.get_or_create(service=service, user=self.user)
            us.calculate_expiration_date(duration=self.subscription.duration, duration_unit=self.subscription.duration_unit)

    def __unicode__(self):
        return u'%s - %s' % (unicode(self.user), unicode(self.subscription))


class UserServiceManager(models.Manager):
    def generate(self, service, user, duration, duration_unit):
        us, _created = UserService.objects.get_or_create(service=service, user=user)
        us.calculate_expiration_date(duration=duration, duration_unit=duration_unit, commit=True)
        return us


class UserService(models.Model):
    """
    User service association. Contains a user, service and an expiration_date
    """
    objects = UserServiceManager()
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

    def calculate_expiration_date(self, duration, duration_unit, commit=True):
        """
        (re)calculate expiration date given a new duration
        """
        today = date.today()
        start_day = today  # start date for calculating duration is by default the current day

        if self.expiration_date is not None:
            if self.expiration_date.date() >= today:
                # expiration date in future ? we increment the given expiration date
                start_day = self.expiration_date.date()

        self.expiration_date = yapremium_utils.calculate_expiration_date(today=start_day, duration=duration, duration_unit=duration_unit)

        # now we can check if the service is available
        if self.expiration_date >= today:
            self.active = True
        else:
            self.active = False

        if commit:
            self.save()

    def as_dict(self):
        data = {
            'id': self.id,
            'service': self.service.get_stype_display(),
            'service_type': self.service.stype,
            'service_id': self.service.id,
            'active': self.active,
            'expiration_date': self.expiration_date,
        }
        return data


class Gift(models.Model):
    """
    A gift can be won by user depending on the action she make
    """
    __metaclass__ = TransMeta

    created = models.DateTimeField(_('created'), auto_now_add=True)
    updated = models.DateTimeField(_('updated'), auto_now=True)
    enabled = models.BooleanField(_('enabled'), default=False)

    name = models.CharField(_('name'), max_length=255, blank=True)
    sku = models.CharField(_('sku'), max_length=255, blank=True)
    description = models.TextField(_('description'), blank=True)

    authentication_needed = models.BooleanField(_('authentication needed'), default=True)
    facebook_needed = models.BooleanField(_('facebook needed'), default=False)
    twitter_needed = models.BooleanField(_('twitter needed'), default=False)
    radio_needed = models.BooleanField(_('radio needed'), default=False)

    action = models.IntegerField(_('action'), choices=yapremium_settings.ACTION_CHOICES)
    action_url_ios = models.TextField(_('iOS action url'), blank=True)  # special field used by iOS to navigate to action menu
    action_url_web = models.TextField(_('web action url'), blank=True)  # special field used by webapp to navigate to action menu
    action_url_web_ajax = models.TextField(_('web action ajax url'), blank=True)  # special field used by webapp to navigate to action menu
    completed_url = models.TextField(_('completed url'), blank=True)  # special field used by webapp to navigate to action menu

    service = models.ForeignKey(Service, verbose_name=_('service'))
    duration = models.IntegerField(_('duration'), default=1)
    duration_unit = models.IntegerField(_('duration unit'), choices=yapremium_settings.DURATION_UNIT_CHOICES, default=yapremium_settings.DURATION_DAY)
    max_per_user = models.IntegerField(_('max per user'), default=1)  # one-shot gift is max_per_user=1

    delay = models.IntegerField(_('delay between 2 gifts (in days)'), blank=True, null=True)

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
        if user is not None and not user.is_anonymous():
            achievements = Achievement.objects.filter(user=user, gift=self).order_by('-achievement_date')
            count = achievements.count()
            if count > 0:
                last_achievement_date = achievements[0].achievement_date

        enabled = True
        if not self.enabled:
            enabled = False
        elif count >= self.max_per_user and self.max_per_user > 0:
            enabled = False

        if self.facebook_needed:
            if user.is_anonymous():
                enabled = False
            if not user.get_profile().facebook_enabled:
                enabled = False

        if self.twitter_needed:
            if user.is_anonymous():
                enabled = False
            if not user.get_profile().twitter_enabled:
                enabled = False

        if self.radio_needed:
            if user.is_anonymous():
                enabled = False
            if Radio.objects.radio_for_user(user) is None:
                enabled = False

        if count > 0:
            picture_url = self.picture_todo_url
        else:
            picture_url = self.picture_done_url

        completed_url = None
        action_url = None
        ajax_url = None
        target = None

        if self.action_url_web:
            try:
                action_url = reverse(self.action_url_web)
            except:
                action_url = self.action_url_web

        if self.completed_url:
            try:
                completed_url = reverse(self.completed_url)
            except:
                completed_url = self.completed_url
        ajax_url = self.action_url_web_ajax

        data = {
            'id': self.id,
            'enabled': enabled,
            'name': self.name,
            'sku': self.sku,
            'description': self.description,
            'max': self.max_per_user,
            'count': count,
            'last_achievement_date': last_achievement_date,
            'picture_url': absolute_url(picture_url),
            'action_url_ios': self.action_url_ios,
            'completed_url': completed_url,
            'action_url': action_url,
            'ajax_url': ajax_url,
            'target': target
        }
        return data

    def __unicode__(self):
        return self.name

    def available(self, user):
        if not self.enabled:
            return False

        if user is not None and not user.is_anonymous():

            achievements = Achievement.objects.filter(user=user, gift=self).order_by('-achievement_date')
            count = achievements.count()
            if count >= self.max_per_user and self.max_per_user > 0:
                return False

            if count > 0 and self.delay is not None:
                now = datetime.now()
                achievement_date = achievements[0].achievement_date
                diff = now - achievement_date
                days = diff.days
                if days <= self.delay:
                    return False

        return True

    class Meta:
        verbose_name = _('gift')
        translate = ('name', 'description',)


class AchievementManager(models.Manager):
    def create_from_gift(self, user, gift, dont_give_anything=False):
        today = date.today()
        obj = self.create(user=user, gift=gift, achievement_date=today)
        us, _created = UserService.objects.get_or_create(user=user, service=gift.service)

        if gift.sku == u'update-account-for-existing-users':
            # special case
            # for users who have created an account before this date,
            # the gift was only 14 days, so we built a fake gift in order to give them 15 days of HD
            if user.date_joined >= datetime(2012, 11, 13, 0, 0):
                dont_give_anything = True
            else:
                logger.info('user %d is an old user, we give him the update account gift' % (user.id))

        if not dont_give_anything:
            us.calculate_expiration_date(duration=gift.duration, duration_unit=gift.duration_unit)
        else:
            us.calculate_expiration_date(duration=0, duration_unit=0)
        return obj


class Achievement(models.Model):
    """
    Store gift won by a user
    """
    objects = AchievementManager()
    created = models.DateTimeField(_('created'), auto_now_add=True)
    updated = models.DateTimeField(_('updated'), auto_now=True)
    user = models.ForeignKey(User, verbose_name=_('user'))
    gift = models.ForeignKey(Gift, verbose_name=_('gift'))
    achievement_date = models.DateTimeField(_('achievement date'))

    def __unicode__(self):
        return u'%s-%s-%s' % (self.user, self.gift, self.achievement_date)

    class Meta:
        verbose_name = _('achievement')


class PromocodeManager(models.Manager):
    def is_valid(self, code, user):
        try:
            promocode = self.get(code=code, enabled=True)
        except Promocode.DoesNotExist:
            return False, None

        if promocode.unique:
            if UserPromocode.objects.filter(promocode=promocode).count() > 0:
                return False, None
        elif UserPromocode.objects.filter(promocode=promocode, user=user).count() > 0:
            return False, None

        return True, promocode

    def create_from_code(self, code, user):
        today = date.today()
        is_valid, promocode = self.is_valid(code=code, user=user)
        if is_valid:
            promocode = self.get(code=code)
            up = UserPromocode.objects.create(user=user, promocode=promocode, usage_date=today)
            UserService.objects.generate(service=promocode.service, user=user, duration=promocode.duration, duration_unit=promocode.duration_unit)
            return up
        return None

    def generate_unique_codes(self, service, duration, count=50, prefix='YA-', group='', duration_unit=yapremium_settings.DURATION_DAY):
        with transaction.commit_on_success():
            for i in range(0, count):
                self.create(code=yapremium_utils.generate_code_name(prefix),
                            enabled=True,
                            service=service,
                            group=group,
                            duration=duration,
                            duration_unit=duration_unit,
                            unique=True)


class PromocodeGroup(models.Model):
    created = models.DateTimeField(_('created'), auto_now_add=True)
    updated = models.DateTimeField(_('updated'), auto_now=True)
    name = models.CharField(_('group'), max_length=100, unique=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('promocode group')


class Promocode(models.Model):
    objects = PromocodeManager()
    created = models.DateTimeField(_('created'), auto_now_add=True)
    updated = models.DateTimeField(_('updated'), auto_now=True)
    code = models.CharField(_('code'), max_length=30, unique=True)
    enabled = models.BooleanField(_('enabled'), default=False)
    service = models.ForeignKey(Service, verbose_name=_('service'))
    duration = models.IntegerField(_('duration'), default=1)
    duration_unit = models.IntegerField(_('duration unit'), choices=yapremium_settings.DURATION_UNIT_CHOICES, default=yapremium_settings.DURATION_MONTH)
    group = models.ForeignKey(PromocodeGroup, verbose_name=_('group'), blank=True, null=True)
    unique = models.BooleanField(_('unique'), default=False)

    def __unicode__(self):
        return self.code

    class Meta:
        verbose_name = _('promocode')


class UserPromocode(models.Model):
    user = models.ForeignKey(User, verbose_name=_('user'))
    promocode = models.ForeignKey(Promocode, verbose_name=_('promo code'))
    usage_date = models.DateTimeField(_('usage date'))

    def __unicode__(self):
        return u'%s - %s' % (self.user, self.promocode)

    class Meta:
        verbose_name = _('user promocode')
        verbose_name_plural = _('user promocodes')


# handlers are used to calculate gift achievements

def new_user_profile_handler(sender, user, **kwargs):
    async_win_gift.delay(user_id=user.id, action=yapremium_settings.ACTION_CREATE_ACCOUNT)
    profile = sender
    if profile is None:
        return

    if profile.yasound_enabled:
        async_check_for_invitation.delay(InvitationsManager.TYPE_EMAIL, user.email)
        async_win_gift.delay(user_id=user.id, action=yapremium_settings.ACTION_ADD_EMAIL_ACCOUNT, dont_give_anything=True)
    if profile.facebook_enabled:
        async_check_for_invitation.delay(InvitationsManager.TYPE_FACEBOOK, profile.facebook_uid)
        async_win_gift.delay(user_id=user.id, action=yapremium_settings.ACTION_ADD_FACEBOOK_ACCOUNT, dont_give_anything=True)
    if profile.twitter_enabled:
        async_win_gift.delay(user_id=user.id, action=yapremium_settings.ACTION_ADD_TWITTER_ACCOUNT, dont_give_anything=True)


def user_profile_updated_handler(sender, instance, created, **kwargs):
    profile = instance
    if profile.is_complete():
        async_win_gift.delay(user_id=profile.user.id, action=yapremium_settings.ACTION_FILL_IN_PROFILE)


def new_radio_ready_handler(sender, radio, **kwargs):
    async_win_gift.delay(user_id=radio.creator.id, action=yapremium_settings.ACTION_CREATE_RADIO)


def facebook_account_added_handler(sender, user, **kwargs):
    async_win_gift.delay(user_id=user.id, action=yapremium_settings.ACTION_ADD_FACEBOOK_ACCOUNT)
    user_profile = UserProfile.objects.get(user=user)
    async_check_for_invitation.delay(InvitationsManager.TYPE_FACEBOOK, user_profile.facebook_uid)


def twitter_account_added_handler(sender, user, **kwargs):
    async_win_gift.delay(user_id=user.id, action=yapremium_settings.ACTION_ADD_TWITTER_ACCOUNT)
    user_profile = UserProfile.objects.get(user=user)
    async_check_for_invitation.delay(InvitationsManager.TYPE_TWITTER, user_profile.twitter_uid)


def user_watched_tutorial_handler(sender, user, **kwargs):
    async_win_gift.delay(user_id=user.id, action=yapremium_settings.ACTION_WATCH_TUTORIAL)


def access_my_radios_handler(sender, user, **kwargs):
    async_win_gift.delay(user_id=user.id, action=yapremium_settings.ACTION_VIEW_STATS)


def access_notifications_handler(sender, user, **kwargs):
    async_win_gift.delay(user_id=user.id, action=yapremium_settings.ACTION_VIEW_NOTIFICATIONS)


def check_for_missed_gifts(sender, request, user, **kwargs):
    """Check if user has missed a gift
    """
    async_win_gift.delay(user_id=user.id, action=yapremium_settings.ACTION_CREATE_ACCOUNT)
    if Radio.objects.filter(creator__id=user.id, ready=True).count() > 0:
        async_win_gift.delay(user_id=user.id, action=yapremium_settings.ACTION_CREATE_RADIO)

    profile = user.get_profile()
    if profile is None:
        return

    if profile.is_complete():
        async_win_gift.delay(user_id=user.id, action=yapremium_settings.ACTION_FILL_IN_PROFILE)

    if profile.is_multi_account:
        if profile.facebook_enabled:
            async_win_gift.delay(user_id=user.id, action=yapremium_settings.ACTION_ADD_FACEBOOK_ACCOUNT)
            if profile.yasound_enabled and profile.twitter_enabled:
                async_win_gift.delay(user_id=user.id, action=yapremium_settings.ACTION_ADD_TWITTER_ACCOUNT)
                async_win_gift.delay(user_id=user.id, action=yapremium_settings.ACTION_ADD_EMAIL_ACCOUNT, dont_give_anything=True)
        elif profile.twitter_enabled:
            if profile.yasound_enabled:
                async_win_gift.delay(user_id=user.id, action=yapremium_settings.ACTION_ADD_TWITTER_ACCOUNT)
                async_win_gift.delay(user_id=user.id, action=yapremium_settings.ACTION_ADD_EMAIL_ACCOUNT, dont_give_anything=True)
    else:
        if profile.facebook_enabled:
            async_win_gift.delay(user_id=user.id, action=yapremium_settings.ACTION_ADD_FACEBOOK_ACCOUNT, dont_give_anything=True)
        elif profile.twitter_enabled:
            async_win_gift.delay(user_id=user.id, action=yapremium_settings.ACTION_ADD_TWITTER_ACCOUNT, dont_give_anything=True)
        elif profile.yasound_enabled:
            async_win_gift.delay(user_id=user.id, action=yapremium_settings.ACTION_ADD_EMAIL_ACCOUNT, dont_give_anything=True)


def new_animator_activity_handler(sender, user, radio, **kwargs):
    if user is None or radio is None:
        return
    if user.is_anonymous():
        return
    async_win_gift.delay(user_id=user.id, action=yapremium_settings.ACTION_UPDATE_PROGRAMMING)


def install_handlers():
    signals.post_save.connect(user_profile_updated_handler, sender=UserProfile)
    account_signals.new_account.connect(new_user_profile_handler)
    account_signals.facebook_account_added.connect(facebook_account_added_handler)
    account_signals.twitter_account_added.connect(twitter_account_added_handler)
    auth_signals.user_logged_in.connect(check_for_missed_gifts)
    yabase_signals.user_watched_tutorial.connect(user_watched_tutorial_handler)
    yabase_signals.access_my_radios.connect(access_my_radios_handler)
    yabase_signals.radio_is_ready.connect(new_radio_ready_handler)
    yabase_signals.new_animator_activity.connect(new_animator_activity_handler)
    yamessage_signals.access_notifications.connect(access_notifications_handler)
install_handlers()
