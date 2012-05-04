import datetime
import os

from django.contrib import sitemaps
from django.core import urlresolvers
from django.conf import settings

class StaticSitemap(sitemaps.Sitemap):
    """Return the static sitemap items"""
    priority = 0.5

    def __init__(self, patterns):
        self.patterns = patterns
        self._items = {}
        self._initialize()

    def protocol(self):
        # will work only in django 1.4
        return settings.DEFAULT_HTTP_PROTOCOL
    
    def _initialize(self):
        for p in self.patterns:
            if getattr(p, 'name', None) is not None and 'template_name' in p.default_args:
                self._items[p.name] = self._get_modification_date(p)

    def _get_modification_date(self, p):
        template = p.default_args['template_name']
        template_path = self._get_template_path(template)
        mtime = os.stat(template_path).st_mtime
        return datetime.datetime.fromtimestamp(mtime)

    def _get_template_path(self, template_path):
        path = os.path.join(settings.PROJECT_PATH + '/apps/yaweb/templates/', template_path)
        if os.path.exists(path):
            return path

        return None

    def items(self):
        return self._items.keys()

    def changefreq(self, obj):
        return 'monthly'

    def lastmod(self, obj):
        return self._items[obj]

    def location(self, obj):
        return urlresolvers.reverse(obj)