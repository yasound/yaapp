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

    if qs.count() > 0:
        yasound_song = qs[0]
    else:
        res = {
            'success': False,
            'message': unicode(_('Cannot match song'))
        }
        return HttpResponse(json.dumps(res))

    add_song(request, radio_id=radio.id, playlist_index=0, yasound_song_id=yasound_song.id)

    res = {'success': True}
    return HttpResponse(json.dumps(res))


class DeezerAppView(View):
    """
    Class based view for deezer in-app.
    """
    def _check_auth(self, request, radio_uuid=None):
        """
        centralized auth checking function,

        return True, None if ok or False, redirect page else
        """
        if settings.ANONYMOUS_ACCESS_ALLOWED == True:
            return True, None

        if not request.user.is_superuser:
            if request.user.groups.filter(name=account_settings.GROUP_NAME_BETATEST).count() == 0:
                if radio_uuid:
                    return False, HttpResponseRedirect(reverse('yabase.views.web_listen', args=[radio_uuid]))
                raise Http404
        return True, None

    def _get_push_url(self, request):
        """
        return absolute url (with port) of push server
        """

        host = request.META['HTTP_HOST']
        protocol = settings.DEFAULT_HTTP_PROTOCOL
        if ':' in host:
            host = host[:host.find(':')]

        url = '%s://%s:%d/' % (protocol, host, settings.YASOUND_PUSH_PORT)
        return url

    def _ajax_success(self):
        data = {
            'success': True
        }
        response = json.dumps(data)
        return HttpResponse(response, mimetype='application/json')

    def _ajax_error(self, errors):
        data = {
            'success': False,
            'errors': errors
        }
        response = json.dumps(data)
        return HttpResponse(response, mimetype='application/json')

    def get(self, request, radio_uuid=None, user_id=None, template_name='deezer/inapp.html', page='home', *args, **kwargs):
        """
        GET method dispatcher. Calls related methods for specific pages
        """
        authorized, redirection = self._check_auth(request, radio_uuid)
        if not authorized:
            return redirection

        notification_count = 0

        my_informations_form = None
        my_accounts_form = None
        my_notifications_form = None
        display_associate_facebook = False
        display_associate_twitter = False

        if request.user.is_authenticated():
            user_profile = request.user.get_profile()
            user_uuid = user_profile.own_radio.uuid

            nm = NotificationsManager()
            notification_count = nm.unread_count(request.user.id)

            display_associate_facebook = not request.user.get_profile().facebook_enabled
            display_associate_twitter = not request.user.get_profile().twitter_enabled
            my_informations_form = MyInformationsForm(instance=UserProfile.objects.get(user=request.user))
            my_accounts_form = MyAccountsForm(instance=UserProfile.objects.get(user=request.user))
            my_notifications_form = MyNotificationsForm(user_profile=request.user.get_profile())

        else:
            user_uuid = 0
            user_profile = None

        push_url = self._get_push_url(request)
        enable_push = settings.ENABLE_PUSH

        facebook_share_picture = absolute_url(settings.FACEBOOK_SHARE_PICTURE)
        facebook_share_link = absolute_url(reverse('webapp'))

        facebook_channel_url = absolute_url(reverse('facebook_channel_url'))

        genre_form = RadioGenreForm()

        has_radios = False
        radio_count = 0
        if request.user.is_authenticated():
            radio_count = request.user.userprofile.own_radios(only_ready_radios=False).count()
        if radio_count > 0:
            has_radios = True

        context = {
            'user_uuid': user_uuid,
            'user_id': user_id,
            'push_url': push_url,
            'enable_push': enable_push,
            'current_uuid': radio_uuid,
            'facebook_app_id': settings.FACEBOOK_APP_ID,
            'facebook_share_picture': facebook_share_picture,
            'facebook_share_link': facebook_share_link,
            'facebook_channel_url': facebook_channel_url,
            'user_profile': user_profile,
            'import_itunes_form': ImportItunesForm(user=request.user),
            'notification_count': notification_count,
            'genre_form': genre_form,
            'has_radios': has_radios,
            'submenu_number': 1,
            'display_associate_facebook': display_associate_facebook,
            'display_associate_twitter': display_associate_twitter,
            'my_informations_form': my_informations_form,
            'my_accounts_form': my_accounts_form,
            'my_notifications_form': my_notifications_form,
            'minutes': get_global_minutes(),
            'deezer_channel_url': absolute_url(reverse('deezer_channel')),
            'deezer_app_id': settings.DEEZER_APP_ID,
        }

        if hasattr(self, page):
            handler = getattr(self, page)
            result = handler(request, context, *args, **kwargs)
            if type(result) == type(()):
                context, template_name = result[0], result[1]
            else:
                return result

        return render_to_response(template_name, context, context_instance=RequestContext(request))

    def post(self, request, radio_uuid=None, query=None, user_id=None, template_name='yabase/webapp.html', page='home', *args, **kwargs):
        """
        POST method dispatcher
        """
        self._check_auth(request, radio_uuid)

        user_uuid = 0
        user_profile = None
        notification_count = 0
        push_url = self._get_push_url(request)
        enable_push = settings.ENABLE_PUSH

        my_informations_form = None
        my_accounts_form = None
        my_notifications_form = None
        display_associate_facebook = False
        display_associate_twitter = False
        if request.user.is_authenticated():
            display_associate_facebook = not request.user.get_profile().facebook_enabled
            display_associate_twitter = not request.user.get_profile().twitter_enabled

        has_radios = False

        facebook_share_picture = absolute_url(settings.FACEBOOK_SHARE_PICTURE)
        facebook_share_link = absolute_url(reverse('webapp'))

        if request.user.is_authenticated():
            user_uuid = request.user.get_profile().own_radio.uuid
            user_profile = request.user.get_profile()
            nm = NotificationsManager()
            notification_count = nm.unread_count(request.user.id)

            radio_count = request.user.userprofile.own_radios(only_ready_radios=False).count()
            if radio_count > 0:
                has_radios = True

        import_itunes_form = ImportItunesForm()

        action = request.REQUEST.get('action')
        if action == 'import_itunes':
            import_itunes_form = ImportItunesForm(request.user, request.POST)
            if import_itunes_form.is_valid():
                import_itunes_form.save()
                if request.is_ajax():
                    return self._ajax_success()
            else:
                if request.is_ajax():
                    return self._ajax_error(import_itunes_form.errors)

        facebook_channel_url = absolute_url(reverse('facebook_channel_url'))

        genre_form = RadioGenreForm()

        context = {
            'user_uuid': user_uuid,
            'user_id': user_id,
            'push_url': push_url,
            'enable_push': enable_push,
            'current_uuid': radio_uuid,
            'facebook_app_id': settings.FACEBOOK_APP_ID,
            'facebook_share_picture': facebook_share_picture,
            'facebook_share_link': facebook_share_link,
            'facebook_channel_url': facebook_channel_url,
            'user_profile': user_profile,
            'import_itunes_form': import_itunes_form,
            'notification_count': notification_count,
            'submenu_number': 1,
            'has_radios': has_radios,
            'genre_form': genre_form,
            'display_associate_facebook': display_associate_facebook,
            'display_associate_twitter': display_associate_twitter,
            'my_informations_form': my_informations_form,
            'my_accounts_form': my_accounts_form,
            'my_notifications_form': my_notifications_form,
            'minutes': get_global_minutes(),
            'deezer_channel_url': absolute_url(reverse('deezer_channel')),
            'deezer_app_id': settings.DEEZER_APP_ID,
        }

        if hasattr(self, page):
            handler = getattr(self, page)
            result = handler(request, context, *args, **kwargs)
            if type(result) == type(()):
                context, template_name = result[0], result[1]
            else:
                return result

        return render_to_response(template_name, context, context_instance=RequestContext(request))
