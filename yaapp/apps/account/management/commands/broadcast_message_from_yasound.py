# -*- coding: utf-8 -*-

from django.conf import settings
from django.core.management.base import BaseCommand
from optparse import make_option
from account.models import UserProfile
from django.contrib.auth.models import User
from yabase.models import Radio


class Command(BaseCommand):
    """
    Send messages to users
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
            from_id = 1
            radio = None
            profiles = UserProfile.objects.all()
            if settings.PRODUCTION_MODE:
                from_id = 2620
                profiles = UserProfile.objects.filter(user__is_superuser=True, user__id=172)
                radio = Radio.objects.get(id=11475)

            default_from = User.objects.get(id=from_id)

            for profile in profiles:
                if profile.language == 'fr':
                    text = u'Félicitations ! Vous avez 1 mois de HD offert pour tester la nouvelle version de YaSound'
                else:
                    text = u'Welcome on YaSound! Play all the radios in HD during 1 month for free'
                profile.send_message(sender=default_from, message=unicode(text), radio=radio)
