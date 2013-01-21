import os

from django.contrib import sitemaps
from django.core import urlresolvers
from django.conf import settings
from datetime import date

class WebappSiteMap(sitemaps.Sitemap):
    """Return the webapp items"""
    priority = 0.5

    STATIC_PAGES = (
        'about',
        'faq',
        'press',
        'jobs',
        'legal',
        'login',
        'passreset',
        'signup',
    )

    def protocol(self):
        # will work only in django 1.4
        return settings.DEFAULT_HTTP_PROTOCOL

    def items(self):
        return WebappSiteMap.STATIC_PAGES

    def changefreq(self, obj):
        if obj in WebappSiteMap.STATIC_PAGES:
            return 'monthly'
        else:
            return 'daily'

    def lastmod(self, obj):
        if obj in WebappSiteMap.STATIC_PAGES:
            return date(2012, 11, 14)

        today = date.today()
        return today

    def location(self, obj):
        return '/%s/' % obj
