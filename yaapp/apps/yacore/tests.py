from django.test import TestCase
from http import is_deezer
from django.test.client import RequestFactory


class TestHttp(TestCase):

    def test_is_deezer(self):
        request = RequestFactory().get('/foo/')
        self.assertFalse(is_deezer(request))

        request.META['HTTP_REFERER'] = 'https://yasound.com/deezer/radio/8f26b61261274264920a53452ac59b19/'
        self.assertTrue(is_deezer(request))
