from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from tastypie.models import ApiKey


def fill_app_infos(request):
    request.app_version = request.REQUEST.get('app_version')
    request.app_id = request.REQUEST.get('app_id')


def is_iphone_version_1(request):
    """check if current user has the v1 version of iPhone app
    """

    app_version = request.REQUEST.get('app_version')
    if app_version is not None:
        app_version.split('.')
        if len(app_version) > 0 and app_version[0] == '1':
            return True
        return False

    user_agent = request.META.get('HTTP_USER_AGENT', '')
    if user_agent.startswith('Yasound 1.'):
        return True
    return False


def is_iphone_version_2(request):
    """check if current user has the v2 version of iPhone app
    """

    app_version = request.REQUEST.get('app_version')
    if app_version:
        app_version.split('.')
        if len(app_version) > 0 and app_version[0] == '2':
            return True
        return False
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    if user_agent.startswith('Yasound 2.'):
        return True
    return False

def is_iphone(request):
    """return True if request is made with iOS
    """
    app_version = request.REQUEST.get('app_version')
    if app_version:
        return True


def is_deezer(request):
    """return True if request is made with deezer inapp. """

    referer = request.META.get('HTTP_REFERER', '')
    if referer.startswith('https://yasound.com/deezer/') or referer.startswith('http://yasound.com/deezer/'):
        return True
    return False


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
    request.app_version = request.REQUEST.get('app_version')
    request.app_id = request.REQUEST.get('app_id')

    if not ('username' in request.REQUEST and 'api_key' in request.REQUEST):
        return False
    username = request.REQUEST.get('username')
    key = request.REQUEST.get('api_key')
    try:
        user = User.objects.get(username=username)
        api_key = ApiKey.objects.get(user=user)
        if api_key.key == key:
            request.user = user
        else:
            return False
    except User.DoesNotExist, ApiKey.DoesNotExist:
        return False

    user.userprofile.authenticated()
    return True


def requested_language(request):
    return request.REQUEST.get('lang')


def check_http_method(request, allowed_methods):
    method = request.method.lower()
    allowed = [x.lower() for x in allowed_methods]
    ok = method in allowed
    return ok


def absolute_url(url):
    """
    return absolute url :

    /myurl --> https://api.yasound.com/myurl

    """
    current_site = Site.objects.get_current()
    protocol = getattr(settings, "DEFAULT_HTTP_PROTOCOL", "http")
    absolute_url = u"%s://%s%s" % (protocol, unicode(current_site.domain), url)
    return absolute_url
