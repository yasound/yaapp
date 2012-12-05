from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import View
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.conf import settings
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render_to_response
from django.template.context import RequestContext
from task import import_playlists_task
from yacore.decorators import check_api_key
from yacore.http import absolute_url
from django.utils.translation import ugettext_lazy as _
from yabase.models import Radio
from yaref.models import YasoundSong
from yabase.views import add_song
from yasearch import utils as yasearch_utils
from yahistory.models import ProgrammingHistory

from yabase.forms import MyAccountsForm, MyInformationsForm, MyNotificationsForm, RadioGenreForm, ImportItunesForm
from yabase.views import get_global_minutes

from account import settings as account_settings
from yamessage.models import NotificationsManager
from account.models import UserProfile
import json
import requests
import logging
logger = logging.getLogger("yaapp.yadeezer")


@csrf_exempt
def deezer_communication(request, username):
    logger.debug('received deezer notification for user %s' % (username))
    get_object_or_404(User, username=username)
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
    """
    dumb view which renders the channel_url file
    """
    return render_to_response(template_name, {
    }, context_instance=RequestContext(request))


@csrf_exempt
@check_api_key(methods=['POST'])
def import_track(request, radio_uuid):
    """
    import deezer track into radio
    """
    radio = get_object_or_404(Radio, uuid=radio_uuid)
    if radio.creator != request.user:
        return HttpResponse(status=403)

    name = request.REQUEST.get('name', '')
    artist_name = request.REQUEST.get('artist_name', '')
    album_name = request.REQUEST.get('album_name', '')

    if name == '' and artist_name == '' and album_name == '':
        res = {
            'success': False,
            'message': unicode(_('Empty query'))
        }
        return HttpResponse(json.dumps(res))

    qs = YasoundSong.objects.all()
    if name != '':
        qs = qs.filter(name_simplified=yasearch_utils.get_simplified_name(name))
    if artist_name != '':
        qs = qs.filter(artist_name_simplified=yasearch_utils.get_simplified_name(artist_name))
    if album_name != '':
        qs = qs.filter(album_name_simplified=yasearch_utils.get_simplified_name(album_name))

    pm = ProgrammingHistory()
    event = pm.generate_event(event_type=ProgrammingHistory.PTYPE_ADD_FROM_DEEZER,
        user=radio.creator,
        radio=radio,
        status=ProgrammingHistory.STATUS_PENDING)

    details = {
        'name': name,
        'artist': artist_name,
        'album': album_name,
    }

    if qs.count() > 0:
        yasound_song = qs[0]
        pm.add_details_success(event, details)
        pm.success(event)
    else:
        pm.add_details_failed(event, details)
        pm.failed(event)
        res = {
            'success': False,
            'message': unicode(_('Cannot match song'))
        }
        return HttpResponse(json.dumps(res))

    add_song(request, radio_id=radio.id, playlist_index=0, yasound_song_id=yasound_song.id)

    res = {'success': True}
    return HttpResponse(json.dumps(res))
