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
            
class Invitation(models.Model):
    objects = InvitationManager()
    fullname = models.CharField(_('Recipient fullname'), max_length=255)
    user = models.OneToOneField(User, verbose_name=_('user'), blank=True, null=True)
    email = models.CharField(_('email'), max_length=255, blank=True)
    key = models.CharField(_('key'), max_length=40, unique=True, blank=True)
    radio = models.ForeignKey(Radio, blank=True, null=True)
    sent = models.DateTimeField(_('sent date'), null=True, blank=True)
    subject = models.CharField(_('subject'), max_length=255, blank=True)
    message = models.TextField(_('message'), blank=True)
    
    def save(self, *args, **kwargs):
        if not self.key:
            salt = sha_constructor(str(random())).hexdigest()[:5]
            self.key = sha_constructor(salt + self.email).hexdigest()
        super(Invitation, self).save(*args, **kwargs)

    def generate_key(self, commit=False):
        salt = sha_constructor(str(random())).hexdigest()[:5]
        self.key = sha_constructor(salt + self.email).hexdigest()
        if commit:
            self.save()
        
    def generate_message(self, commit=False):
        if not self.key:
            self.generate_key(commit=True)
            
        path = reverse("yainvitation_accept", args=[self.key])
        current_site = Site.objects.get_current()
        protocol = getattr(settings, "DEFAULT_HTTP_PROTOCOL", "http")
        invitation_url = u"%s://%s%s" % (
            protocol,
            unicode(current_site.domain),
            path
        )
        context = {
            "fullname": self.fullname,
            "email": self.email,
            "invitation_url": invitation_url,
            "current_site": current_site,
            "key": self.key,
        }
        subject = render_to_string("yainvitation/mail/email_invitation_subject.txt", context)
        
        # remove superfluous line breaks
        subject = "".join(subject.splitlines())
        message = render_to_string("yainvitation/mail/email_invitation_message.txt", context)
        
        if commit:
            self.subject = subject
            self.message = message
            self.save()
        return subject, message 
            
            
    def send(self):
        if not self.message:
            self.generate_message()
        self.sent = datetime.datetime.now()
        send_mail(self.subject, self.message, settings.DEFAULT_FROM_EMAIL, [self.email])
        self.save()
    
    def __unicode__(self):
        return self.email
    
    class Meta:
        verbose_name = _('invitation')

    





