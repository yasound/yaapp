from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import settings as yaweb_settings
import mimetypes, os
from django_mobile import get_flavour

import logging
logger = logging.getLogger("yaapp.yaweb")


@csrf_exempt
def index(request, template_name='yaweb/index.html', template_name_mobile='yaweb/index_mobile.html'):
    if request.method == 'POST':
        logger.info('received POST request for index page : %s' % request.REQUEST)
        
    if get_flavour() == 'mobile':
        template_name = template_name_mobile

    return render_to_response(template_name, {
        'current_page': 'index',
        'production_mode': settings.PRODUCTION_MODE
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

def eula(request, template_name='yaweb/eula.html'):
    return render_to_response(template_name, {
        'current_page': 'eula',
    }, context_instance=RequestContext(request))  

def privacy(request, template_name='yaweb/privacy.html'):
    return render_to_response(template_name, {
        'current_page': 'privacy',
    }, context_instance=RequestContext(request))  

def elecsounds(request, template_name='yaweb/elecsounds.html'):
    return render_to_response(template_name, {
        'current_page': 'elecsounds',
    }, context_instance=RequestContext(request))  

def elecsounds_terms(request, template_name='yaweb/elecsounds_terms.html'):
    return render_to_response(template_name, {
        'current_page': 'elecsounds_terms',
    }, context_instance=RequestContext(request))  

def elecsounds_winner(request, template_name='yaweb/elecsounds_winner.html'):
    return render_to_response(template_name, {
        'current_page': 'elecsounds_winner',
    }, context_instance=RequestContext(request))  

def contest_station(request, template_name='yaweb/contest_station.html'):
    return render_to_response(template_name, {
        'current_page': 'contest_station',
    }, context_instance=RequestContext(request))  

def contest_station_terms(request, template_name='yaweb/contest_station_terms.html'):
    return render_to_response(template_name, {
        'current_page': 'contest_station_terms',
    }, context_instance=RequestContext(request))  

def contest_station_iphone(request, template_name='yaweb/contest_station_iphone.html'):
    return render_to_response(template_name, {
        'current_page': 'contest_station_iphone',
    }, context_instance=RequestContext(request))  

def logo(request):
    return HttpResponseRedirect('/media/yaweb/images/logo.png')


def download(request, filename):
    file = open(filename,"r")
    mimetype = mimetypes.guess_type(filename)[0]
    if not mimetype: mimetype = "application/octet-stream"

    response = HttpResponse(file.read(), mimetype=mimetype)
    response["Content-Disposition"]= "attachment; filename=%s" % os.path.split(filename)[1]
    return response

