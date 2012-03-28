from django.conf import settings
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand
from django.core.urlresolvers import reverse
from facepy import GraphAPI
from optparse import make_option
from yabase import task
from yabase.models import Playlist, Radio, SongMetadata
from yaref.models import YasoundSong
from yaref.utils import queryset_iterator
import logging
import requests


logger = logging.getLogger("yaapp.account")

class Command(BaseCommand):
    """
    Extract covers
    """
    option_list = BaseCommand.option_list + (
        make_option('-l', '--list', dest='list', action='store_true',
            default=False, help="list: display subscriptions"),
        make_option('-c', '--cancel', dest='cancel', action='store_true',
            default=False, help="cancel subscription"),
        make_option('-s', '--subscribe', dest='subscribe', action='store_true',
            default=False, help="request subscription"),
    )
    help = "Subscribe to facebook realtime updates"
    args = ''

    def handle(self, *app_labels, **options):
        action_list = options.get('list', False)
        action_cancel = options.get('cancel', False)
        action_subscribe = options.get('subscribe', False)
        
        url = 'https://graph.facebook.com/oauth/access_token?client_id=%s&client_secret=%s&grant_type=client_credentials' % (settings.FACEBOOK_APP_ID, settings.FACEBOOK_API_SECRET)
        res = requests.get(url)
        content = res.text
        access_token = None
        if 'access_token=' in content:
            access_token = content[len('access_token='):]
        if not access_token:
            logger.error("cannot find access token: %s" % content)
            return

        graph = GraphAPI(access_token)
        if action_list:
            logger.info('list current subscriptions')
            res = graph.get('subscriptions')
            logger.info(res)
        elif action_cancel:
            logger.info('delete current subscriptions')
            graph.delete('subscriptions')
        elif action_subscribe:
            logger.info('request subscription')
            current_site = Site.objects.get_current()
            protocol = getattr(settings, "DEFAULT_HTTP_PROTOCOL", "https")
            callback_url = u"%s://%s%s" % (
                protocol,
                unicode(current_site.domain),
                reverse('facebook_update')
            )
            res = graph.post('subscriptions', 
                             object='user', 
                             fields='email,friends,name', 
                             callback_url=callback_url,
                             verify_token=settings.FACEBOOK_REALTIME_VERIFY_TOKEN) 
            logger.info(res)
        logger.info("done")        
        
        
