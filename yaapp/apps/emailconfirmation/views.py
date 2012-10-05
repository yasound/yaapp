from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext
from emailconfirmation.models import EmailConfirmation



def confirm_email(request, confirmation_key):
    
    confirmation_key = confirmation_key.lower()
    email_address = EmailConfirmation.objects.confirm_email(confirmation_key)
    if email_address:
        user = email_address.user
        user.is_active = True
        user.save()
        email_address.user.backend='django.contrib.auth.backends.ModelBackend'
        login(request, email_address.user)
        return HttpResponseRedirect(reverse('webapp_default'))
    return render_to_response("emailconfirmation/confirm_email.html", {
        "email_address": email_address,
    }, context_instance=RequestContext(request))