from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.conf import settings
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render_to_response
from django.template.context import RequestContext
from task import import_playlists_task

import requests
import logging
logger = logging.getLogger("yaapp.yadeezer")


@csrf_exempt
def deezer_communication(request, username):
    logger.debug('received deezer notification for user %s' % (username))
    _user = get_object_or_404(User, username=username)
    code = request.REQUEST.get('code', '')
    reason = request.REQUEST.get('reason', '')

    if reason != '' and code == '':
        logger.info('reason is not empty (%s), exiting' % (reason))
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

def channel_url(request, template_name='deezer/channel_url.html'):
    return render_to_response(template_name, {
    }, context_instance=RequestContext(request))

