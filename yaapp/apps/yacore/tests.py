from django.test import TestCase
from http import is_deezer
from django.test.client import RequestFactory
import cache as yacore_cache
from django.contrib.auth.models import User
from yabase.models import Radio


class TestHttp(TestCase):
    def test_is_deezer(self):
        request = RequestFactory().get('/foo/')
        self.assertFalse(is_deezer(request))

        request.META['HTTP_REFERER'] = 'https://yasound.com/deezer/radio/8f26b61261274264920a53452ac59b19/'
        self.assertTrue(is_deezer(request))


class TestCache(TestCase):
    def test_own_radio_cache(self):
        user = User(email="test@yasound.com", username="test", is_superuser=False, is_staff=False)
        user.set_password('test')
        user.save()

        # build some data
        radio = Radio(creator=user, name='radio1')
        radio.save()

        yacore_cache.cache_object(key='key', obj=radio)

        self.assertIsNone(yacore_cache.cached_object(key='key2'))

        self.assertEquals(yacore_cache.cached_object(key='key').id, radio.id)

        yacore_cache.invalidate_object(key='key2')
        self.assertEquals(yacore_cache.cached_object(key='key').id, radio.id)

        yacore_cache.invalidate_object(key='key')
        self.assertIsNone(yacore_cache.cached_object(key='key'))

        r = user.get_profile().own_radio
        self.assertEquals(r.id, radio.id)

        r = yacore_cache.cached_object(key='user_%d.own_radio' % (user.id))
        self.assertEquals(r.id, radio.id)
