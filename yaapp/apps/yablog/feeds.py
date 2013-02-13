from django.contrib.syndication.views import Feed
from models import BlogPost
from django.utils.translation import ugettext as _


class LatestPostFeed(Feed):
    title = _("YaSound blog feed")
    link = "/news/feeds/"
    description = "Updates on changes and additions to yasound.com/blog."

    def items(self):
        return BlogPost.objects.get_posts()[:10]

    def item_title(self, item):
        return item.name

    def item_description(self, item):
        return item.get_description()
