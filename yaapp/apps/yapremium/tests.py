from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from yapremium.models import Subscription, UserSubscription, Service, UserService, Gift, Achievement, Promocode, UserPromocode
from task import check_expiration_date
import settings as yapremium_settings
from datetime import *
from dateutil.relativedelta import *
from account import signals as account_signals
from utils import verify_receipt, generate_code_name
import json


class TestModel(TestCase):
    def setUp(self):
        user = User(email="test@yasound.com", username="test", is_superuser=True, is_staff=True)
        user.set_password('test')
        user.save()
        self.client.login(username="test", password="test")
        self.user = user

    def test_available(self):
        self.assertEquals(len(Subscription.objects.available_subscriptions()), 0)

        sub = Subscription.objects.create(name='sub', sku='sub')
        self.assertFalse(sub.enabled)

        self.assertEquals(len(Subscription.objects.available_subscriptions()), 0)
        sub.enabled = True
        sub.save()
        self.assertEquals(len(Subscription.objects.available_subscriptions()), 1)

    def test_subscribe(self):
        today = date.today()
        subscription = Subscription.objects.create(name='sub', sku='sub', duration=2, enabled=True)

        us = UserSubscription.objects.create(subscription=subscription, user=self.user)
        self.assertEquals(us.expiration_date, today + relativedelta(months=+subscription.duration))


class TestVerifyReceipt(TestCase):
    def setUp(self):
        user = User(email="test@yasound.com", username="test", is_superuser=True, is_staff=True)
        user.set_password('test')
        user.save()
        self.client.login(username="test", password="test")
        self.user = user

    def test_verify_receipt(self):
        f = open('./apps/yapremium/fixtures/yasound_inapp_apple_receipt.bin')
        data = f.read()
        f.close()
        self.assertTrue(verify_receipt(data, encode=True))


class TestView(TestCase):
    def setUp(self):
        user = User(email="test@yasound.com", username="test", is_superuser=True, is_staff=True)
        user.set_password('test')
        user.save()
        self.client.login(username="test", password="test")
        self.user = user

    def test_get_subscriptions(self):
        sub = Subscription.objects.create(name='sub', sku_en='com.yasound.yasound.inappHD1y', enabled=True)

        res = self.client.get(reverse('yapremium.views.subscriptions'))
        self.assertEquals(res.status_code, 200)
        data = json.loads(res.content)
        self.assertEquals(data.get('meta').get('total_count'), 1)

        res = self.client.post(reverse('yapremium.views.subscriptions', kwargs={'subscription_sku': sub.sku}))
        self.assertEquals(res.status_code, 403)

    def test_get_gifts(self):
        service = Service.objects.create(stype=yapremium_settings.SERVICE_HD)
        gift = Gift.objects.create(name='gift',
            description='description',
            service=service,
            action=yapremium_settings.ACTION_WATCH_TUTORIAL,
            enabled=True)

        res = self.client.get(reverse('yapremium.views.gifts'))
        self.assertEquals(res.status_code, 200)
        data = json.loads(res.content)
        self.assertEquals(data.get('meta').get('total_count'), 1)

        item = data.get('objects')[0]
        self.assertTrue(item.get('enabled'))
        self.assertEquals(item.get('count'), 0)
        self.assertEquals(item.get('max'), 1)

        achievement = Achievement.objects.create(user=self.user, gift=gift, achievement_date=datetime(2012, 8, 24, 0, 0))

        res = self.client.get(reverse('yapremium.views.gifts'))
        self.assertEquals(res.status_code, 200)
        data = json.loads(res.content)
        self.assertEquals(data.get('meta').get('total_count'), 1)

        item = data.get('objects')[0]
        self.assertFalse(item.get('enabled'))
        self.assertEquals(item.get('count'), 1)
        self.assertEquals(item.get('max'), 1)
        self.assertEquals(item.get('last_achievement_date'), '2012-08-24T00:00:00')

        self.client.logout()

        res = self.client.get(reverse('yapremium.views.gifts'))
        self.assertEquals(res.status_code, 200)
        data = json.loads(res.content)
        self.assertEquals(data.get('meta').get('total_count'), 1)

        item = data.get('objects')[0]
        self.assertTrue(item.get('enabled'))


class TestGift(TestCase):
    def setUp(self):
        user = User(email="test@yasound.com", username="test", is_superuser=True, is_staff=True)
        user.set_password('test')
        user.save()
        self.client.login(username="test", password="test")
        self.user = user

    def test_create_account(self):
        user2 = User.objects.create(email="user2@yasound.com", username="user2")
        self.assertFalse(user2.get_profile().permissions.hd)

        service = Service.objects.create(stype=yapremium_settings.SERVICE_HD)
        gift = Gift.objects.create(name='gift',
            description='description',
            service=service,
            action=yapremium_settings.ACTION_CREATE_ACCOUNT,
            duration=2,
            duration_unit=yapremium_settings.DURATION_DAY,
            max_per_user=1,
            enabled=True)

        user3 = User.objects.create(email="user3@yasound.com", username="user3")
        self.assertTrue(user3.get_profile().permissions.hd)

        us = UserService.objects.get(user=user3, service=service)
        self.assertTrue(us.active)

        today = date.today()
        two_days = today + relativedelta(days=+2)
        self.assertEquals(us.expiration_date.date(), two_days)

    def test_add_facebook_account(self):
        user2 = User.objects.create(email="user2@yasound.com", username="user2")
        self.assertFalse(user2.get_profile().permissions.hd)

        service = Service.objects.create(stype=yapremium_settings.SERVICE_HD)
        gift = Gift.objects.create(name='gift',
            description='description',
            service=service,
            action=yapremium_settings.ACTION_ADD_FACEBOOK_ACCOUNT,
            duration=1,
            max_per_user=1,
            enabled=True)

        account_signals.facebook_account_added.send(sender=user2.get_profile(), user=user2)

        user2 = User.objects.get(id=user2.id)  # reload object
        self.assertTrue(user2.get_profile().permissions.hd)

        us = UserService.objects.get(user=user2, service=service)
        self.assertTrue(us.active)

        today = date.today()
        one_month = today + relativedelta(months=+1)
        self.assertEquals(us.expiration_date.date(), one_month)

    def test_add_twitter_account(self):
        user2 = User.objects.create(email="user2@yasound.com", username="user2")
        self.assertFalse(user2.get_profile().permissions.hd)

        service = Service.objects.create(stype=yapremium_settings.SERVICE_HD)
        gift = Gift.objects.create(name='gift',
            description='description',
            service=service,
            action=yapremium_settings.ACTION_ADD_TWITTER_ACCOUNT,
            duration=1,
            max_per_user=1,
            enabled=True)

        account_signals.twitter_account_added.send(sender=user2.get_profile(), user=user2)

        user2 = User.objects.get(id=user2.id)  # reload object
        self.assertTrue(user2.get_profile().permissions.hd)

        us = UserService.objects.get(user=user2, service=service)
        self.assertTrue(us.active)

        today = date.today()
        one_month = today + relativedelta(months=+1)
        self.assertEquals(us.expiration_date.date(), one_month)


class TestExpirationDate(TestCase):
    def setUp(self):
        user = User(email="test@yasound.com", username="test", is_superuser=True, is_staff=True)
        user.set_password('test')
        user.save()
        self.client.login(username="test", password="test")
        self.user = user

    def test_generate_service_for_user(self):
        today = date.today()
        service = Service.objects.create(stype=yapremium_settings.SERVICE_HD)
        subscription = Subscription.objects.create(name='sub', sku='com.yasound.yasound.inappHD1y', enabled=True)
        subscription.services.add(service)

        us = UserSubscription.objects.create(subscription=subscription, user=self.user)
        self.assertEquals(us.expiration_date, today + relativedelta(months=+subscription.duration))

        us = UserSubscription.objects.get(subscription=subscription, user=self.user)
        user_service = UserService.objects.get(user=self.user, service=service)
        self.assertTrue(user_service.active)
        self.assertEquals(user_service.expiration_date, us.expiration_date)

    def test_check_expiration_date(self):
        today = date.today()
        service = Service.objects.create(stype=yapremium_settings.SERVICE_HD)
        subscription = Subscription.objects.create(name='sub', sku='com.yasound.yasound.inappHD1y', enabled=True)
        subscription.services.add(service)

        us = UserSubscription.objects.create(subscription=subscription, user=self.user)
        self.assertEquals(us.expiration_date, today + relativedelta(months=+subscription.duration))

        us = UserSubscription.objects.get(subscription=subscription, user=self.user)
        user_service = UserService.objects.get(user=self.user, service=service)

        # check when date is ok
        check_expiration_date()
        user_service = UserService.objects.get(user=self.user, service=service)
        self.assertTrue(user_service.active)

        # check when date is expired
        user_service.expiration_date = today + relativedelta(months=-12)
        user_service.save()

        self.assertTrue(user_service.active)

        check_expiration_date()
        user_service = UserService.objects.get(user=self.user, service=service)
        self.assertFalse(user_service.active)


class TestPromocode(TestCase):
    def setUp(self):
        user = User(email="test@yasound.com", username="test", is_superuser=True, is_staff=True)
        user.set_password('test')
        user.save()
        self.client.login(username="test", password="test")
        self.user = user

    def test_is_valid_with_bad_code(self):

        is_valid, promocode = Promocode.objects.is_valid(code='toto', user=self.user)
        self.assertFalse(is_valid)
        self.assertIsNone(promocode)

    def test_is_valid_with_good_code(self):
        service = Service.objects.create(stype=yapremium_settings.SERVICE_HD)
        promocode = Promocode.objects.create(code='code', duration=12, service=service, enabled=True)
        is_valid, promocode2 = Promocode.objects.is_valid(code='code', user=self.user)
        self.assertTrue(is_valid)
        self.assertEquals(promocode2.id, promocode.id)

    def test_is_valid_without_unique(self):
        user2 = User.objects.create(email="user2@yasound.com", username="user2")
        today = date.today()
        service = Service.objects.create(stype=yapremium_settings.SERVICE_HD)
        promocode = Promocode.objects.create(code='code', duration=12, service=service, enabled=True)

        up = UserPromocode.objects.create(user=self.user, usage_date=today, promocode=promocode)

        is_valid, promocode2 = Promocode.objects.is_valid(code='code', user=self.user)
        self.assertFalse(is_valid)
        self.assertIsNone(promocode2)

        is_valid, promocode2 = Promocode.objects.is_valid(code='code', user=user2)
        self.assertTrue(is_valid)
        self.assertIsNotNone(promocode2)

    def test_is_valid_with_unique2(self):
        user2 = User.objects.create(email="user2@yasound.com", username="user2")
        today = date.today()
        service = Service.objects.create(stype=yapremium_settings.SERVICE_HD)
        promocode = Promocode.objects.create(code='code', duration=12, service=service, enabled=True, unique=True)

        up = UserPromocode.objects.create(user=self.user, usage_date=today, promocode=promocode)

        is_valid, promocode2 = Promocode.objects.is_valid(code='code', user=user2)
        self.assertFalse(is_valid)
        self.assertIsNone(promocode2)

    def test_create_from_bad_code(self):
        service = Service.objects.create(stype=yapremium_settings.SERVICE_HD)
        promocode = Promocode.objects.create(code='code', duration=12, service=service)

        up = Promocode.objects.create_from_code(code='toutou', user=self.user)
        self.assertIsNone(up)


    def test_create_from_good_code(self):
        today = date.today()
        service = Service.objects.create(stype=yapremium_settings.SERVICE_HD)
        promocode = Promocode.objects.create(code='code', duration=12, service=service, enabled=True)
        promocode2 = Promocode.objects.create(code='code2', duration=24, service=service, enabled=True)

        up = Promocode.objects.create_from_code(code='code', user=self.user)
        self.assertIsNotNone(up)

        us = UserService.objects.get(service=service, user=self.user)
        self.assertEquals(us.expiration_date.date(), today + relativedelta(months=+promocode.duration))

        up = Promocode.objects.create_from_code(code='code2', user=self.user)
        self.assertIsNotNone(up)

        us = UserService.objects.get(service=service, user=self.user)
        self.assertEquals(us.expiration_date.date(), today + relativedelta(months=+promocode.duration+promocode2.duration))

    def test_view(self):
        today = date.today()
        service = Service.objects.create(stype=yapremium_settings.SERVICE_HD)

        res = self.client.post(reverse('yapremium.views.activate_promocode'), {'code': 'code1'})
        self.assertEquals(res.status_code, 200)
        data = json.loads(res.content)
        self.assertEquals(data.get('success'), False)

        promocode = Promocode.objects.create(code='code', duration=12, service=service, enabled=True)

        res = self.client.post(reverse('yapremium.views.activate_promocode'), {'code': 'code'})
        self.assertEquals(res.status_code, 200)
        data = json.loads(res.content)
        self.assertEquals(data.get('success'), True)

        us = UserService.objects.get(service=service, user=self.user)
        self.assertEquals(us.expiration_date.date(), today + relativedelta(months=+promocode.duration))

    def test_generate_code_name(self):
        code_name = generate_code_name(prefix='YA-')
        self.assertEquals(len(code_name), 9)
        self.assertEquals(code_name[:3], 'YA-')
