from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.context import RequestContext


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
