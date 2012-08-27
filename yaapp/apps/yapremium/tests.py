from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from yapremium.models import Subscription, UserSubscription
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

        us = UserSubscription.objects.create(subscription=subscription, user=self.user, active=True)
        self.assertTrue(us.active)
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
