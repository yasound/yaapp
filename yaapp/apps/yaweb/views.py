from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
import settings as yaweb_settings
import mimetypes, os

def index(request, template_name='yaweb/index.html'):
    return render_to_response(template_name, {
        'current_page': 'index',
    }, context_instance=RequestContext(request))  


def about(request, template_name='yaweb/about.html'):
    return render_to_response(template_name, {
        'current_page': 'about',
    }, context_instance=RequestContext(request))  

def jobs(request, template_name='yaweb/jobs.html'):
    return render_to_response(template_name, {
        'current_page': 'jobs',
    }, context_instance=RequestContext(request))  

def press(request, template_name='yaweb/press.html'):
    return render_to_response(template_name, {
        'current_page': 'press',
    }, context_instance=RequestContext(request))  

def contact(request, template_name='yaweb/contact.html'):
    return render_to_response(template_name, {
        'current_page': 'contact',
    }, context_instance=RequestContext(request))  

def redirect(request, url=''):
    redirected_url = '/' + url
    urls = yaweb_settings.REDIRECT_URLS
    
    if url in urls:
        redirected_url = reverse(urls[url]) 
    return HttpResponseRedirect(redirected_url)

def download(request, filename):
    file = open(filename,"r")
    mimetype = mimetypes.guess_type(filename)[0]
    if not mimetype: mimetype = "application/octet-stream"

    response = HttpResponse(file.read(), mimetype=mimetype)
    response["Content-Disposition"]= "attachment; filename=%s" % os.path.split(filename)[1]
    return response