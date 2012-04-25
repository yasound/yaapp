from tastypie.models import ApiKey
from django.contrib.auth.models import User

def coerce_put_post(request):
    """
    Django doesn't particularly understand REST.
    In case we send data over PUT, Django won't
    actually look at the data and load it. We need
    to twist its arm here.
   
    The try/except abominiation here is due to a bug
    in mod_python. This should fix it.
    """
    if request.method == "PUT":
        # Bug fix: if _load_post_and_files has already been called, for
        # example by middleware accessing request.POST, the below code to
        # pretend the request is a POST instead of a PUT will be too late
        # to make a difference. Also calling _load_post_and_files will result
        # in the following exception:
        #   AttributeError: You cannot set the upload handlers after the upload has been processed.
        # The fix is to check for the presence of the _post field which is set
        # the first time _load_post_and_files is called (both by wsgi.py and
        # modpython.py). If it's set, the request has to be 'reset' to redo
        # the query value parsing in POST mode.
        if hasattr(request, '_post'):
            del request._post
            del request._files

        try:
            request.method = "POST"
            request._load_post_and_files()
            request.method = "PUT"
        except AttributeError:
            request.META['REQUEST_METHOD'] = 'POST'
            request._load_post_and_files()
            request.META['REQUEST_METHOD'] = 'PUT'

        request.PUT = request.POST    
        
        

def check_api_key_Authentication(request):
    if not ('username' in request.GET and 'api_key' in request.GET):
        return False
    username = request.GET['username']
    key = request.GET['api_key']
    try:
        user = User.objects.get(username=username)
        api_key = ApiKey.objects.get(user=user)
        if api_key.key == key:
            request.user =user
        else:
            return False
    except User.DoesNotExist, ApiKey.DoesNotExist:
        return False
    
    user.userprofile.authenticated()
    return True

def check_http_method(request, allowed_methods):
    allowed = request.method in allowed_methods or request.method.lower() in allowed_methods or request.method.higher() in allowed_methods
    return allowed
        