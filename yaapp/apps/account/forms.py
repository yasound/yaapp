# -*- coding:utf-8 -*-
from captcha.fields import CaptchaField
from django import forms
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.models import get_current_site
from django.template import Context, loader
from django.template.loader import render_to_string
from django.utils.encoding import smart_unicode
from django.utils.http import int_to_base36
from django.utils.translation import ugettext_lazy as _, ugettext
from emailconfirmation.models import EmailAddress, EmailTemplate
from hashlib import sha1
from models import UserProfile, EmailUser
from random import choice
from string import letters
from yacore.geoip import request_country, can_login
import re
alnum_re = re.compile(r'^\w+$')


def _generate_password():
    from random import choice
    import string
    size = 12
    password = ''.join([choice(string.letters + string.digits) for i in range(size)])
    return password


class LoginForm(forms.Form):

    email = forms.CharField(label=_("Email"), max_length=75, widget=forms.TextInput(attrs={'placeholder': _('Email')}))
    password = forms.CharField(label=_("Password"), widget=forms.PasswordInput(render_value=False, attrs={'placeholder': _('Password')}))
    user = None

    def clean(self):
        if self._errors:
            return
        user = authenticate(username=self.cleaned_data["email"], password=self.cleaned_data["password"])
        if user:
            if user.is_active:
                self.user = user
            else:
                raise forms.ValidationError(_("This account is currently inactive."))
        else:
            raise forms.ValidationError(_("The username and/or password you specified are not correct."))
        return self.cleaned_data

    def login(self, request):
        if can_login(request):
            if self.is_valid():
                login(request, self.user)
                request.session.set_expiry(60 * 60 * 24 * 7 * 3)
                return True
        return False
    

class LostPasswordForm(forms.Form):
    login = forms.CharField(label=_('Email'), max_length=256, help_text=_('Enter your email or login'))

class UserForm(forms.Form):

    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        super(UserForm, self).__init__(*args, **kwargs)

class UserProfileForm(UserForm):
    
    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        try:
            self.account = UserProfile.objects.get(user=self.user)
        except UserProfile.DoesNotExist:
            self.account = UserProfile(user=self.user)

class ChangeLanguageForm(UserProfileForm):

    language = forms.ChoiceField(label=_("Language"), required=True, choices=settings.LANGUAGES)

    def __init__(self, *args, **kwargs):
        super(ChangeLanguageForm, self).__init__(*args, **kwargs)
        self.initial.update({"language": self.account.language})

    def save(self):
        self.account.language = self.cleaned_data["language"]
        self.account.save()
        self.user.message_set.create(message=ugettext(u"Language successfully updated."))

class SignupForm(forms.Form):
    username = forms.CharField(label=_("Username"), widget=forms.TextInput(attrs={'placeholder': _('Username')}))
    email = forms.EmailField(label=_("Email"), required=True, widget=forms.TextInput(attrs={'placeholder': _('Email')}))
    password1 = forms.CharField(label=_("Password"), widget=forms.PasswordInput(attrs={'placeholder': _('Password')}))
        
    def clean_username(self):
        profiles = UserProfile.objects.filter(name__exact=self.cleaned_data["username"])
        if profiles.count() > 0:
            raise forms.ValidationError(u"This username is already taken. Please choose another.")
        return self.cleaned_data["username"]
    
    def clean_email(self):
        user = User.objects.filter(email__exact=self.cleaned_data["email"])
        if not user:
            
            return self.cleaned_data["email"]
        raise forms.ValidationError(u"This email is already taken. Please choose another.")

    def save(self):
        from api import build_random_username
        
        email = self.cleaned_data["email"]
        password = self.cleaned_data["password1"]
        username = build_random_username()
        if email and username:
            new_user = EmailUser.objects.create_user(username, email, password)
            user = EmailUser.objects.get(email=email)
            user.is_active = False
            user.save()
            
            user.get_profile().name = self.cleaned_data["username"]
            user.get_profile().save()
            
            EmailAddress.objects.add_email(new_user, email)
            
            return username, email
        return False

class FastSignupForm(forms.Form):
    """
    Fast and anonymous signup form for creating unactive anonymous users
    """
    email = forms.EmailField(label="Email", required=True, widget=forms.TextInput())
    firstname = forms.CharField(label="First name", max_length=30, widget=forms.TextInput())
    lastname = forms.CharField(label="Last name", max_length=30, widget=forms.TextInput())
    password1 = forms.CharField(label=_("Password"), required=False, widget=forms.PasswordInput())
    password2 = forms.CharField(label=_("Password (again)"), required=False, widget=forms.PasswordInput())
    create_account = forms.BooleanField(label=_("Create an account with these informations ?"), required=False)
    newsletter_accepted = forms.BooleanField(label=_("Register to newsletter ?"), required=False)
        
    def clean_email(self):
        user = EmailUser.objects.filter(email__exact=self.cleaned_data["email"], userprofile__anonymous=False)
        if not user:
            return self.cleaned_data["email"]
        raise forms.ValidationError(u"This email is already taken. Please choose another.")

    def clean(self):
        if "password1" in self.cleaned_data and "password2" in self.cleaned_data:
            if self.cleaned_data["password1"] != self.cleaned_data["password2"]:
                raise forms.ValidationError(u"You must type the same password each time.")
            
        return self.cleaned_data
        
    def save(self):
        email = self.cleaned_data["email"]
        password = self.cleaned_data["password1"]
        create_account = self.cleaned_data['create_account']
        username = sha1(str(email)).hexdigest()[:30]
        if not create_account:
            password = _generate_password()
            username = ''.join([choice(letters) for i in xrange(30)])
        if email:
            user = EmailUser.objects.create_user(username, email, password)
            user.last_name = self.cleaned_data['lastname']
            user.first_name = self.cleaned_data['firstname']
            user.is_active = False
            user.save()
            # profile is automatically created by signal
            profile = UserProfile.objects.get(user=user)
            profile.newsletter_accepted = self.cleaned_data['newsletter_accepted']
            profile.anonymous = not create_account
            profile.save()
            if create_account:
                EmailAddress.objects.add_email(user, email)
            return user, email
        return False


class AddEmailForm(forms.Form):
    
    def __init__(self, data=None, user=None):
        super(AddEmailForm, self).__init__(data=data)
        self.user = user
    
    email = forms.EmailField(label="Email", required=True, widget=forms.TextInput())
    
    def clean_email(self):
        try:
            EmailAddress.objects.get(user=self.user, email=self.cleaned_data["email"])
        except EmailAddress.DoesNotExist:
            return self.cleaned_data["email"]
        raise forms.ValidationError(u"This email address already associated with this account.")
    
    def save(self):
        self.user.message_set.create(message="Confirmation email sent to %s" % self.cleaned_data["email"])
        return EmailAddress.objects.add_email(self.user, self.cleaned_data["email"])
        
class PasswordResetForm(forms.Form):
    email = forms.EmailField(widget=forms.TextInput(attrs={'placeholder': _('Email')}), max_length=75)

    def clean_email(self):
        """
        Validates that an active user exists with the given e-mail address.
        """
        email = self.cleaned_data["email"]
        self.users_cache = User.objects.filter(
                                email__iexact=email,
                                is_active=True
                            )
        if len(self.users_cache) == 0:
            raise forms.ValidationError(_("That e-mail address doesn't have an associated user account. Are you sure you've registered?"))
        return email

    def save(self, domain_override=None, email_template_name='registration/password_reset_email.html',
             use_https=False, token_generator=default_token_generator, from_email=None, request=None):
        """
        Generates a one-use only link for resetting password and sends to the user
        """
        from django.core.mail import send_mail
        for user in self.users_cache:
            if not domain_override:
                current_site = get_current_site(request)
                site_name = current_site.name
                domain = current_site.domain
            else:
                site_name = domain = domain_override
            c = {
                'email': user.email,
                'domain': domain,
                'site_name': site_name,
                'uid': int_to_base36(user.id),
                'user': user,
                'token': token_generator.make_token(user),
                'protocol': use_https and 'https' or 'http',
            }
            
            subject, message = EmailTemplate.objects.generate_mail(EmailTemplate.EMAIL_TYPE_LOST, c)
            send_mail(subject, message, from_email, [user.email])
        
class ChangePasswordForm(UserForm):

    oldpassword = forms.CharField(label=_("Current Password"), widget=forms.PasswordInput(render_value=False))
    password1 = forms.CharField(label=_("New Password"), widget=forms.PasswordInput(render_value=False))
    password2 = forms.CharField(label=_("New Password (again)"), widget=forms.PasswordInput(render_value=False))
    
    def clean_oldpassword(self):
        if not self.user.check_password(self.cleaned_data.get("oldpassword")):
            raise forms.ValidationError(_("Please type your current password."))
        return self.cleaned_data["oldpassword"]

    def clean_password2(self):
        if "password1" in self.cleaned_data and "password2" in self.cleaned_data:
            if self.cleaned_data["password1"] != self.cleaned_data["password2"]:
                raise forms.ValidationError(_("You must type the same password each time."))
        return self.cleaned_data["password2"]

    def save(self):
        self.user.set_password(self.cleaned_data['password1'])
        self.user.save()
        self.user.message_set.create(message=ugettext(u"Password successfully changed."))
        
class SetPasswordForm(forms.Form):
    """
    A form that lets a user change set his/her password without
    entering the old password
    """
    new_password1 = forms.CharField(label=_("New password"), widget=forms.PasswordInput)
    new_password2 = forms.CharField(label=_("New password confirmation"), widget=forms.PasswordInput)

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(SetPasswordForm, self).__init__(*args, **kwargs)

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(_("The two password fields didn't match."))
        return password2

    def save(self, commit=True):
        self.user.set_password(self.cleaned_data['new_password1'])
        if commit:
            self.user.save()
        return self.user
