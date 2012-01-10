from tastypie.models import ApiKey
from django.contrib.auth.models import User

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
    return True

def check_http_method(request, allowed_methods):
    allowed = request.method in allowed_methods or request.method.lower() in allowed_methods or request.method.higher() in allowed_methods
    return allowed