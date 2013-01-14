from django.contrib.sitemaps import Sitemap
from models import BlogPost


class BlogPostSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.5

    def items(self):
        return BlogPost.objects.get_posts()

    def lastmod(self, obj):
        return obj.updated
