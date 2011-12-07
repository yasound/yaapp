from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
from models import Post

def all(request):
  csrfContext = RequestContext(request)
  posts = Post.objects.all().order_by('-date')
  return render_to_response('wall/allposts.html', {'posts': posts}, csrfContext)

def write(request):
  csrfContext = RequestContext(request)
  return render_to_response('wall/write.html', csrfContext)
    
@csrf_exempt
def sendpost(request):
  author = request.POST['author']
  password = request.POST['password']
  kind = request.POST['kind']
  #if len(tpe) == 0
  #kind = "text"
  user = authenticate(username=author, password=password)
  if user is not None:
    if user.is_active:
      login(request, user)
      posttext = request.POST['posttext']
      p = Post()
      p.kind = kind
      p.author = user
      p.data = posttext
      p.date = datetime.now()
      p.save()
      # Always return an HttpResponseRedirect after successfully dealing
      # with POST data. This prevents data from being posted twice if a
      # user hits the Back button.
  return HttpResponseRedirect(reverse('yaapp.wall.views.all'))

@csrf_exempt
def allAPI(request):
  posts = Post.objects.all().order_by('date')
  return render_to_response('wall/all.xml', {'posts': posts})

@csrf_exempt
def sendpostAPI(request):
  author = request.POST['author']
  password = request.POST['password']
  kind = request.POST['kind']
  #if len(tpe) == 0
  #kind = "text"
  user = authenticate(username=author, password=password)
  if user is not None:
    if user.is_active:
      login(request, user)
      posttext = request.POST['posttext']
      p = Post()
      p.author = user
      p.data = posttext
      p.kind = kind
      p.date = datetime.now()
      p.save()
  return allAPI(request)

