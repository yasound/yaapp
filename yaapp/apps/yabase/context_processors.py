from django.conf import settings


def facebook(request):
    return {
        'FACEBOOK_APP_ID': settings.FACEBOOK_APP_ID,
        'FACEBOOK_APP_NAMESPACE': settings.FACEBOOK_APP_NAMESPACE
    }
