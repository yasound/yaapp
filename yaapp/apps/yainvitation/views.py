from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse, HttpResponseNotFound, \
    HttpResponseNotAllowed, HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from models import Invitation

@login_required
def accept(request, key, template_name='yainvitation/accept.html'):
    invitation = get_object_or_404(Invitation, key=key)    
    invitation.accept(request.user)
    
    return render_to_response(template_name, {
    }, context_instance=RequestContext(request))    
    
