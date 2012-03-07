from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.core.urlresolvers import reverse, NoReverseMatch
from django.db import models
from django.template.loader import render_to_string
from django.utils.hashcompat import sha_constructor
from django.utils.translation import ugettext_lazy as _
from yabase.models import Radio
import datetime
from random import random

class InvitationManager(models.Manager):
    def pending(self):
        return self.filter(sent__isnull=True)

    def sent(self):
        return self.filter(sent__isnull=False, user__isnull=True)
    
    def accepted(self):
        return self.filter(sent__isnull=False, user__isnull=False)
        
    def send_invitation(self, fullname, email, radio):
        salt = sha_constructor(str(random())).hexdigest()[:5]
        key = sha_constructor(salt + email).hexdigest()
        path = reverse("yainvitation_accept", args=[key])
        current_site = Site.objects.get_current()
        protocol = getattr(settings, "DEFAULT_HTTP_PROTOCOL", "http")
        invitation_url = u"%s://%s%s" % (
            protocol,
            unicode(current_site.domain),
            path
        )
        context = {
            "fullname": fullname,
            "email": email,
            "invitation_url": invitation_url,
            "current_site": current_site,
            "key": key,
        }
        subject = render_to_string("yainvitation/mail/email_invitation_subject.txt", context)
        
        # remove superfluous line breaks
        subject = "".join(subject.splitlines())
        message = render_to_string("yainvitation/mail/email_invitation_message.txt", context)
        
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])
        invitation = self.create(
            email=email,
            sent=datetime.datetime.now(),
            key=key,
            radio=radio,
            fullname=fullname,
        )
        return invitation
    
class Invitation(models.Model):
    objects = InvitationManager()
    fullname = models.CharField(_('Recipient fullname'), max_length=255)
    user = models.OneToOneField(User, verbose_name=_('user'), blank=True, null=True)
    email = models.CharField(_('email'), max_length=255, unique=True)
    key = models.CharField(_('key'), max_length=40, unique=True, blank=True)
    radio = models.ForeignKey(Radio)
    sent = models.DateTimeField(_('sent date'), null=True, blank=True)
    
    def __unicode__(self):
        return self.email
    
    class Meta:
        verbose_name = _('invitation')

    





