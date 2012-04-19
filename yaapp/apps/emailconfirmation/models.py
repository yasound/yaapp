import datetime
from random import random

from django.conf import settings
from django.db import models, IntegrityError
from django.core.mail import send_mail
from django.core.urlresolvers import reverse, NoReverseMatch
from django.template.loader import render_to_string
from django.utils.hashcompat import sha_constructor
from django.utils.translation import gettext_lazy as _

from django.contrib.sites.models import Site
from django.contrib.auth.models import User

from emailconfirmation.signals import email_confirmed, email_confirmation_sent

from django.template import Context, Template

from transmeta import TransMeta

# this code based in-part on django-registration

class EmailAddressManager(models.Manager):
    
    def add_email(self, user, email):
        try:
            email_address = self.create(user=user, email=email)
            EmailConfirmation.objects.send_confirmation(email_address)
            return email_address
        except IntegrityError:
            return None
    
    def get_primary(self, user):
        try:
            return self.get(user=user, primary=True)
        except EmailAddress.DoesNotExist:
            return None
    
    def get_users_for(self, email):
        """
        returns a list of users with the given email.
        """
        # this is a list rather than a generator because we probably want to
        # do a len() on it right away
        return [address.user for address in EmailAddress.objects.filter(
            verified=True, email=email)]


class EmailAddress(models.Model):
    
    user = models.ForeignKey(User)
    email = models.EmailField()
    verified = models.BooleanField(default=False)
    primary = models.BooleanField(default=False)
    
    objects = EmailAddressManager()
    
    def set_as_primary(self, conditional=False):
        old_primary = EmailAddress.objects.get_primary(self.user)
        if old_primary:
            if conditional:
                return False
            old_primary.primary = False
            old_primary.save()
        self.primary = True
        self.save()
        self.user.email = self.email
        self.user.save()
        return True
    
    def __unicode__(self):
        return u"%s (%s)" % (self.email, self.user)
    
    class Meta:
        verbose_name = _("email address")
        verbose_name_plural = _("email addresses")
        unique_together = (
            ("user", "email"),
        )


class EmailConfirmationManager(models.Manager):
    
    def confirm_email(self, confirmation_key):
        try:
            confirmation = self.get(confirmation_key=confirmation_key)
        except self.model.DoesNotExist:
            return None
        if not confirmation.key_expired():
            email_address = confirmation.email_address
            email_address.verified = True
            email_address.set_as_primary(conditional=True)
            email_address.save()
            email_confirmed.send(sender=self.model, email_address=email_address)
            return email_address
    
    def send_confirmation(self, email_address):
        salt = sha_constructor(str(random())).hexdigest()[:5]
        confirmation_key = sha_constructor(salt + email_address.email).hexdigest()
        current_site = Site.objects.get_current()
        # check for the url with the dotted view path
        try:
            path = reverse("emailconfirmation.views.confirm_email",
                args=[confirmation_key])
        except NoReverseMatch:
            # or get path with named urlconf instead
            path = reverse(
                "emailconfirmation_confirm_email", args=[confirmation_key])
        protocol = getattr(settings, "DEFAULT_HTTP_PROTOCOL", "http")
        activate_url = u"%s://%s%s" % (
            protocol,
            unicode(current_site.domain),
            path
        )
        context = {
            "user": email_address.user,
            "activate_url": activate_url,
            "current_site": current_site,
            "confirmation_key": confirmation_key,
        }
        
        subject, message = EmailTemplate.objects.generate_mail(EmailTemplate.EMAIL_TYPE_FIRST, context)

        # remove superfluous line breaks
        subject = "".join(subject.splitlines())
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email_address.email])
        confirmation = self.create(
            email_address=email_address,
            sent=datetime.datetime.now(),
            confirmation_key=confirmation_key
        )
        email_confirmation_sent.send(
            sender=self.model,
            confirmation=confirmation,
        )
        return confirmation
    
    def delete_expired_confirmations(self):
        for confirmation in self.all():
            if confirmation.key_expired():
                if not confirmation.email_address.verified and confirmation.email_address.primary:
                    user = User.objects.get(id=confirmation.email_address.user.id)
                    user.is_active = False
                    user.save()

                    # send an email
                    try:
                        subject = 'user %d disabled' % (user.id)
                        message = 'the user %d (username = %s, email: %s) has been disabled because of missing confirmation' % (user.id, user.username, user.email)
                        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, settings.MANAGERS)
                    except:
                        pass
                    
                confirmation.delete()
    
    def resend_confirmations(self):
        for confirmation in self.all():
            if confirmation.resend_expired() and not confirmation.email_address.verified:
                confirmation.resend()

class EmailConfirmation(models.Model):
    objects = EmailConfirmationManager()
    
    email_address = models.ForeignKey(EmailAddress)
    sent = models.DateTimeField()
    confirmation_key = models.CharField(max_length=40)
    retries = models.SmallIntegerField(default=0)

    def resend_expired(self):
        expiration_date = self.sent + datetime.timedelta(
            days=settings.EMAIL_RESEND_CONFIRMATION_DAYS)
        return expiration_date <= datetime.datetime.now() and self.retries == 0
    resend_expired.boolean = True
    
    def key_expired(self):
        expiration_date = self.sent + datetime.timedelta(
            days=settings.EMAIL_CONFIRMATION_DAYS)
        return expiration_date <= datetime.datetime.now()
    key_expired.boolean = True
    
    def resend(self):
        confirmation_key = self.confirmation_key
        email_address = self.email_address
        
        current_site = Site.objects.get_current()
        # check for the url with the dotted view path
        try:
            path = reverse("emailconfirmation.views.confirm_email",
                args=[confirmation_key])
        except NoReverseMatch:
            # or get path with named urlconf instead
            path = reverse(
                "emailconfirmation_confirm_email", args=[confirmation_key])
        protocol = getattr(settings, "DEFAULT_HTTP_PROTOCOL", "http")
        activate_url = u"%s://%s%s" % (
            protocol,
            unicode(current_site.domain),
            path
        )
        context = {
            "user": email_address.user,
            "activate_url": activate_url,
            "current_site": current_site,
            "confirmation_key": confirmation_key,
        }
        subject, message = EmailTemplate.objects.generate_mail(EmailTemplate.EMAIL_TYPE_LAST, context)

        # remove superfluous line breaks
        subject = "".join(subject.splitlines())
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email_address.email])
        self.retries = self.retries + 1
        self.save()
        
    def __unicode__(self):
        return u"confirmation for %s" % self.email_address
    
    class Meta:
        verbose_name = _("email confirmation")
        verbose_name_plural = _("email confirmations")
        

class EmailTemplateManager(models.Manager):
    
    def generate_mail(self, email_type, context_dict):
        """
        return subject, mail
        """
        try:
            template = self.get(email_type=email_type, activated=True)
        except:
            return '', ''
        
        
        tpl_subject = Template(template.subject)
        tpl_body = Template(template.body)
        
        context = Context(context_dict)
        
        return tpl_subject.render(context), tpl_body.render(context) 
        
        
class EmailTemplate(models.Model):
    objects = EmailTemplateManager()

    __metaclass__ = TransMeta

    subject = models.CharField(_('subject'), max_length=255)
    body = models.TextField(_('body'))
    activated = models.BooleanField(_('activated'), default=True)
    
    EMAIL_TYPE_FIRST = 0 
    EMAIL_TYPE_LAST = 1
    EMAIL_TYPE_LOST = 2
    EMAIL_TYPE_CHOICES = (
        (EMAIL_TYPE_FIRST, _('First confirmation email')),
        (EMAIL_TYPE_LAST, _('Last confirmation mail')),
        (EMAIL_TYPE_LOST, _('Lost password email')),
    )
    
    email_type = models.SmallIntegerField(choices=EMAIL_TYPE_CHOICES, default=EMAIL_TYPE_FIRST)
    
    class Meta:
        translate = ('subject', 'body',)    
    
    def save(self, *args, **kwargs):
        if self.activated:
            EmailTemplate.objects.filter(email_type=self.email_type).exclude(id=self.id).update(activated=False)
        super(EmailTemplate, self).save(*args, **kwargs)
    
