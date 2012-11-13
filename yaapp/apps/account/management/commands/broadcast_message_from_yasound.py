from django.conf import settings
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand
from django.core.urlresolvers import reverse
from optparse import make_option
from account.models import UserProfile

class Command(BaseCommand):
    """
    Extract covers
    """
    option_list = BaseCommand.option_list + (
        make_option('-u', '--url', dest='url',
            default=None, help="url: url to open in message"),
        make_option('-t', '--text', dest='text',
            default=None, help="text: text to send"),
    )
    help = "broadcast a message from yasound to all users"
    args = ''

    def handle(self, *app_labels, **options):
        url_param = options.get('url', None)
        text = options.get('text', None)
        if not url_param and not text:
            return

        if url_param is not None:
            UserProfile.objects.broadcast_message_from_yasound(url_param)

        if text:
            default_from = UserProfile.objects.get(id=1).user
            profiles = UserProfile.objects.all()
            for profile in profiles:
                profile.send_message(sender=default_from, message=text)


