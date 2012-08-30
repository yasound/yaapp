from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.conf import settings
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from task import import_playlists_task
import requests
import logging
logger = logging.getLogger("yaapp.account")


@csrf_exempt
def deezer_communication(request, username):
    logger.debug('received deezer notification for user %s' % (username))
    username = get_object_or_404(User, username=username)
    code = request.REQUEST.get('code', '')
    reason = request.REQUEST.get('reason', '')

    logger.debug('code = %s, reason=%s' % (code, reason))

    if reason != '' and code == '':
        logger.debug('reason is not empty, exiting')
        return HttpResponse('OK')

    params = {
        'app_id': settings.DEEZER_APP_ID,
        'secret': settings.DEEZER_SECRET_KEY,
        'code': code,
    }
    try:
        r = requests.get(settings.DEEZER_CONNECT_URL, params=params)
        data = r.text
    except:
        logger.error('cannot communicate with deezer with params = %r' % (params))
        return HttpResponse('OK')

    token = None
    try:
        token = data.split('=')[1].split('?')[0].split('&')[0]
    except:
        logger.info('cannot parse token')
        pass
    if token is None:
        return HttpResponse('OK')
    logger.info('token is %s' % (token))
    logger.info('launching playlists import')
    import_playlists_task.delay(username, token)
    return HttpResponse('OK')
