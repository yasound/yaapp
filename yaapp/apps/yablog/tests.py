from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from models import BlogPost
from sitemaps import BlogPostSitemap
from datetime import datetime


class TestBlogPost(TestCase):
    def setUp(self):
        user = User(email="bear@localhost", username="bear", is_superuser=False, is_staff=False)
        user.set_password('bear')
        user.save()
        self.client.login(username="bear", password="bear")
        self.user = user

    def testGetBlogPost(self):
        response = self.client.get(reverse('webapp_default_blog_posts'))
        self.assertEquals(response.status_code, 200)
        posts = response.context['blog_posts']
        self.assertEquals(len(posts), 0)

        post = BlogPost(name='post',
                        slug='slug',
                        creator=self.user,
                        description='dummy',
                        state=BlogPost.STATE_PUBLISHED,
                        publish_date=datetime(2007, 12, 5))
        post.save()

        response = self.client.get(reverse('webapp_default_blog_posts'))
        self.assertEquals(response.status_code, 200)
        posts = response.context['blog_posts']
        self.assertEquals(len(posts), 1)

    def testStickyBlogPost(self):
        response = self.client.get(reverse('webapp_default_blog_posts'))
        self.assertEquals(response.status_code, 200)
        posts = response.context['blog_posts']
        self.assertEquals(len(posts), 0)

        post1 = BlogPost(name='post1',
                         slug='post1',
                         creator=self.user,
                         description='dummy',
                         state=BlogPost.STATE_PUBLISHED,
                         publish_date=datetime(2007, 12, 5))
        post1.save()

        post2 = BlogPost(name='post2',
                         slug='post2',
                         creator=self.user,
                         sticky=False,
                         description='dummy',
                         state=BlogPost.STATE_PUBLISHED,
                         publish_date=datetime(2007, 12, 2))
        post2.save()

        response = self.client.get(reverse('webapp_default_blog_posts'))
        self.assertEquals(response.status_code, 200)
        posts = response.context['blog_posts']
        self.assertEquals(len(posts), 2)
        self.assertEquals(posts[0], post1)

        post2.sticky = True
        post2.save()

        response = self.client.get(reverse('webapp_default_blog_posts'))
        self.assertEquals(response.status_code, 200)
        posts = response.context['blog_posts']
        self.assertEquals(len(posts), 2)
        self.assertEquals(posts[0], post2)

    def testSitemap(self):
        post1 = BlogPost(name='post1',
                         slug='post1',
                         creator=self.user,
                         description='dummy',
                         state=BlogPost.STATE_DRAFT,
                         publish_date=datetime(2007, 12, 5))
        post1.save()
        post2 = BlogPost(name='post2',
                         slug='post2',
                         creator=self.user,
                         description='ymmud',
                         state=BlogPost.STATE_PUBLISHED,
                         publish_date=datetime(2007, 12, 5))
        post2.save()

        # Test if not in sitemap
        response = self.client.get('/sitemap.xml')
        self.assertNotIn('post1', response.content)

        # Test if in sitemap
        self.assertIn('post2', response.content)
