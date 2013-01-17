from datetime import datetime
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404, \
    get_list_or_404
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _
from models import BlogPost
from yacore.api import api_response, api_response_raw
from yacore.decorators import check_api_key


def index(request, template_name='news/index.html'):
    posts = BlogPost.objects.get_news()
    return render_to_response(template_name, {
        "posts": posts,
    }, context_instance=RequestContext(request))


def post(request, year, month, day, slug, template_name='news/post.html'):
    post = get_object_or_404(BlogPost, slug=slug)

    if not request.user.is_superuser:
        if post.state != BlogPost.STATE_PUBLISHED:
            raise Http404
        now = datetime.now()
        if post.publish_date > now:
            raise Http404

    return render_to_response(template_name, {
        "post": post,
    }, context_instance=RequestContext(request))


@check_api_key(methods=['GET'], login_required=False)
def posts(request, slug=None):
    if request.method == 'GET' and slug is None:
        qs = BlogPost.objects.get_posts()
        data = []
        for post in qs:
            post_dict = post.as_dict()
            data.append(post_dict)

        response = api_response(data, len(data))
        return response
    elif request.method == 'GET' and slug is not None:
        post = get_object_or_404(BlogPost, slug=slug)
        post_dict = post.as_dict()
        data = []
        data.append(post_dict)
        response = api_response(data, len(data))
        return response

    raise Http404
