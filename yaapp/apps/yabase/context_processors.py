from yabase.models import Radio
from django.conf import settings

def my_radios(request):
    if not request.user.is_authenticated():
        return []
    
    radios = Radio.objects.filter(creator=request.user, ready=True)
    return {
        'my_radios': radios
    }
    
def facebook(request):
    return {
        'FACEBOOK_APP_ID': settings.FACEBOOK_APP_ID,
        'FACEBOOK_APP_NAMESPACE': settings.FACEBOOK_APP_NAMESPACE
    }
