from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from yapremium.models import Subscription, UserSubscription, Service, UserService
from task import check_expiration_date
import settings as yapremium_settings
from datetime import *
from dateutil.relativedelta import *

from utils import verify_receipt
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
        sub = Subscription.objects.create(name='sub', sku='com.yasound.yasound.inappHD1y', enabled=True)

        res = self.client.get(reverse('yapremium.views.subscriptions'))
        self.assertEquals(res.status_code, 200)
        data = json.loads(res.content)
        self.assertEquals(data.get('meta').get('total_count'), 1)

        res = self.client.post(reverse('yapremium.views.subscriptions', args=[sub.sku,]))
        self.assertEquals(res.status_code, 403)

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





