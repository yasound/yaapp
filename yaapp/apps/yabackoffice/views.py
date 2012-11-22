from account import export as account_export
from account.models import UserProfile, Device
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, UserManager
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.core import serializers
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.db.models import Q, Count
from django.db.models.aggregates import Sum, Count
from django.http import HttpResponseRedirect, HttpResponseRedirect, HttpResponse, \
    HttpResponseForbidden, Http404
from django.shortcuts import render_to_response, get_object_or_404, \
    get_list_or_404
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from emailconfirmation.models import EmailConfirmation, EmailAddress
from emencia.django.newsletter.models import Contact
from extjs import utils
from grids import SongInstanceGrid, RadioGrid, \
    InvitationGrid, YasoundSongGrid, PromocodeGrid, CountryGrid, GeoFeatureGrid
from yabackoffice.forms import RadioForm, InvitationForm
from yabackoffice.grids import UserProfileGrid, WallEventGrid
from yabackoffice.models import BackofficeRadio
from yabase import settings as yabase_settings
from yabase.models import Radio, SongInstance, WallEvent, RadioUser, \
    SongMetadata
from yacore.api import MongoAwareEncoder, MongoAwareEncoder, api_response
from yacore.http import coerce_put_post
from yainvitation.models import Invitation
from yametrics.models import GlobalMetricsManager, TopMissingSongsManager, \
    TimedMetricsManager, UserMetricsManager, AbuseManager
from yaref import task
from yaref.models import YasoundSong
import datetime
import requests
import simplejson as json
import utils as yabackoffice_utils
from yasearch.models import MostPopularSongsManager
from yametrics.matching_errors import MatchingErrorsManager
from yabase.export_utils import export_pur
from yapremium import export as yapremium_export
from yahistory.models import UserHistory
from yasearch.utils import get_simplified_name
from yapremium.models import Promocode, Service, PromocodeGroup
from yapremium import settings as yapremium_settings
from yageoperm.models import Country, GeoFeature
from django.db import IntegrityError
from stats import export as stats_export
import xlwt
import StringIO

@login_required
def index(request, template_name="yabackoffice/index.html"):
    if not request.user.is_superuser:
        raise Http404()

    return render_to_response(template_name, {
    }, context_instance=RequestContext(request))

@csrf_exempt
@login_required
def radio_unmatched_song(request, radio_id):
    if not request.user.is_superuser:
        raise Http404()

    radio = get_object_or_404(Radio, id=radio_id)
    if request.method == 'GET':
        qs = radio.unmatched_songs
        grid = SongInstanceGrid()
        jsonr = yabackoffice_utils.generate_grid_rows_json(request, grid, qs)
        resp = utils.JsonResponse(jsonr)
        return resp

@csrf_exempt
@login_required
def radio_songs(request, radio_id):
    if not request.user.is_superuser:
        raise Http404()
    radio = get_object_or_404(Radio, id=radio_id)
    if request.method == 'GET':
        qs = SongInstance.objects.filter(playlist__radio=radio)

        yasound_song_id = request.REQUEST.get('yasound_song_id')

        filters = [('name', 'metadata__name'),
                   ('artist_name', 'metadata__artist_name'),
                   ('album_name', 'metadata__album_name')]
        if yasound_song_id:
            qs = qs.filter(metadata__yasound_song_id=yasound_song_id)
        grid = SongInstanceGrid()
        jsonr = yabackoffice_utils.generate_grid_rows_json(request, grid, qs, filters)
        resp = utils.JsonResponse(jsonr)
        return resp

@csrf_exempt
@login_required
def radio_remove_songs(request, radio_id):
    """
    delete song instance from radio
    """
    if not request.user.is_superuser:
        raise Http404()
    radio = get_object_or_404(Radio, id=radio_id)
    if request.method == 'POST':
        ids = request.REQUEST.getlist('song_instance_id')
        radio.delete_song_instances(ids)
        json_data = json.JSONEncoder(ensure_ascii=False).encode({
            'success': True,
            'message': ''
        })
        return HttpResponse(json_data, mimetype='application/json')
    raise Http404

@csrf_exempt
@login_required
def radio_remove_all_songs(request, radio_id):
    """
    delete all song instance from radio
    """
    if not request.user.is_superuser:
        raise Http404()
    radio = get_object_or_404(Radio, id=radio_id)
    if request.method == 'POST':
        SongInstance.objects.filter(playlist__radio=radio).delete()
        json_data = json.JSONEncoder(ensure_ascii=False).encode({
            'success': True,
            'message': ''
        })
        return HttpResponse(json_data, mimetype='application/json')
    raise Http404

@csrf_exempt
@login_required
def radio_remove_duplicate_songs(request, radio_id):
    """
    delete duplicate song instance from radio
    """
    if not request.user.is_superuser:
        raise Http404()
    radio = get_object_or_404(Radio, id=radio_id)
    if request.method == 'POST':
        playlist, _created = radio.get_or_create_default_playlist()
        qs = SongInstance.objects.filter(playlist=playlist).order_by('metadata')
        duplicates = []
        prev_metadata = None
        for si in qs:
            if si.metadata == prev_metadata and prev_metadata is not None:
                duplicates.append(si.id)
            prev_metadata = si.metadata

        radio.delete_song_instances(duplicates)

        json_data = json.JSONEncoder(ensure_ascii=False).encode({
            'success': True,
            'message': ''
        })
        return HttpResponse(json_data, mimetype='application/json')
    raise Http404

@csrf_exempt
@login_required
def radio_add_songs(request, radio_id):
    """
    add yasound song to radio
    """
    if not request.user.is_superuser:
        raise Http404()
    radio = get_object_or_404(Radio, id=radio_id)
    if request.method == 'POST':
        ids = request.REQUEST.getlist('yasound_song_id')
        yasound_songs = YasoundSong.objects.filter(id__in=ids)
        playlist, _created = radio.get_or_create_default_playlist()
        for yasound_song in yasound_songs:
            SongInstance.objects.create_from_yasound_song(playlist, yasound_song)
        radio.ready=True
        radio.save()
        json_data = json.JSONEncoder(ensure_ascii=False).encode({
            'success': True,
            'message': ''
        })
        return HttpResponse(json_data, mimetype='application/json')
    raise Http404

@csrf_exempt
@login_required
def radio_duplicate(request, radio_id):
    """
    add yasound song to radio
    """
    if not request.user.is_superuser:
        raise Http404()
    radio = get_object_or_404(Radio, id=radio_id)
    if request.method == 'POST':
        radio.duplicate()
        json_data = json.JSONEncoder(ensure_ascii=False).encode({
            'success': True,
            'message': ''
        })
        return HttpResponse(json_data, mimetype='application/json')
    raise Http404

@csrf_exempt
@login_required
def radio_blacklist(request, radio_id):
    """
    blacklist radio
    """
    if not request.user.is_superuser:
        raise Http404()
    radio = get_object_or_404(Radio, id=radio_id)
    if request.method == 'POST':
        radio.blacklisted = True
        radio.save()
        json_data = json.JSONEncoder(ensure_ascii=False).encode({
            'success': True,
            'message': ''
        })
        return HttpResponse(json_data, mimetype='application/json')
    raise Http404

@csrf_exempt
@login_required
def radio_unblacklist(request, radio_id):
    """
    unblacklist radio
    """
    if not request.user.is_superuser:
        raise Http404()
    radio = get_object_or_404(Radio, id=radio_id)
    if request.method == 'POST':
        radio.blacklisted = False
        radio.save()
        json_data = json.JSONEncoder(ensure_ascii=False).encode({
            'success': True,
            'message': ''
        })
        return HttpResponse(json_data, mimetype='application/json')
    raise Http404


@csrf_exempt
@login_required
def radio_export_stats(request, radio_id):
    """
    export radio stats
    """
    if not request.user.is_superuser:
        raise Http404
    radio = get_object_or_404(Radio, id=radio_id)
    if request.method == 'POST':
        data = stats_export.export_radio_stats(radio)
        response = HttpResponse(data, mimetype='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename=stats_%d.xls' % (radio.id)
        return response
    raise Http404


@csrf_exempt
@login_required
def radios(request, radio_id=None):
    if not request.user.is_superuser:
        raise Http404()
    if request.method == 'GET':
        qs = BackofficeRadio.objects.all()

        rtype = request.REQUEST.get('rtype', None)
        if rtype == 'latest':
            qs = qs.order_by('-id')
            grid = RadioGrid()
            (start, limit) = yabackoffice_utils.get_limit(request)
            jsonr = grid.get_rows_json(qs, start=start, limit=limit)
            resp = utils.JsonResponse(jsonr)
            return resp
        elif rtype == 'biggest':
            qs = Radio.objects.annotate(song_count=Count('playlists__songinstance')).order_by('-song_count')
            grid = RadioGrid()
            (start, limit) = yabackoffice_utils.get_limit(request)
            jsonr = grid.get_rows_json(qs, start=start, limit=limit)
            resp = utils.JsonResponse(jsonr)
            return resp

        filters = ['id', 'name', ('creator_profile', 'creator__userprofile__name')]
        grid = RadioGrid()
        jsonr = yabackoffice_utils.generate_grid_rows_json(request, grid, qs, filters=filters)
        resp = utils.JsonResponse(jsonr)
        return resp
    elif request.method == 'POST':
        data = request.REQUEST.get('data')
        decoded_data = json.loads(data)
        form = RadioForm(decoded_data)
        errors = None
        success = True
        message = ''
        if form.is_valid():
            radio = form.save()
            qs = BackofficeRadio.objects.filter(id=radio.id)
            grid = RadioGrid()
            jsonr = yabackoffice_utils.generate_grid_rows_json(request, grid, qs)
            resp = utils.JsonResponse(jsonr)
            return resp
        else:
            message = _("Invalid input")
            errors = form.errors
            success = False

            json_data = json.JSONEncoder(ensure_ascii=False).encode({
                'success': success,
                'errors': errors,
                'message': message,
            })
            return utils.JsonResponse(json_data)
    elif request.method == 'DELETE':
        radio = get_object_or_404(Radio, id=radio_id)
        radio.empty_next_songs_queue()
        radio.mark_as_deleted()
        data = {"success":True,"message":"ok","data":[]}
        resp = utils.JsonResponse(json.JSONEncoder(ensure_ascii=False).encode(data))
        return resp
    raise Http404


@csrf_exempt
@login_required
def invitations(request, type='all', invitation_id=None):
    if not request.user.is_superuser:
        raise Http404()
    if request.method == 'GET':
        if type == 'all':
            qs = Invitation.objects.all()
        elif type == 'pending':
            qs = Invitation.objects.pending()
        elif type == 'sent':
            qs = Invitation.objects.sent()
        elif type == 'accepted':
            qs = Invitation.objects.accepted()
        else:
            qs = Invitation.objects.all()

        grid = InvitationGrid()
        filters = ['fullname',
                   'email',
                   ('radio', 'radio__name'),
                   ('user_profile',  'user__profile__name')]
        jsonr = yabackoffice_utils.generate_grid_rows_json(request, grid, qs, filters)
        resp = utils.JsonResponse(jsonr)
        return resp
    elif request.method == 'POST':
        data = request.REQUEST.get('data')
        decoded_data = json.loads(data)
        form = InvitationForm(decoded_data)
        errors = None
        success = True
        message = ''
        if form.is_valid():
            invitation = form.save()
            invitation.generate_message(commit=True)
            qs = Invitation.objects.filter(id=invitation.id)
            grid = InvitationGrid()
            jsonr = yabackoffice_utils.generate_grid_rows_json(request, grid, qs)
            resp = utils.JsonResponse(jsonr)
            return resp
        else:
            message = _("Invalid input")
            errors = form.errors
            success = False

            json_data = json.JSONEncoder(ensure_ascii=False).encode({
                'success': success,
                'errors': errors,
                'message': message,
            })
            return utils.JsonResponse(json_data)
    elif request.method == 'DELETE':
        invitation = get_object_or_404(Invitation, id=invitation_id)
        invitation.delete()
        data = {"success":True,"message":"ok","data":[]}
        resp = utils.JsonResponse(json.JSONEncoder(ensure_ascii=False).encode(data))
        return resp

@csrf_exempt
@login_required
def invitation_generate_message(request, invitation_id):
    if not request.user.is_superuser:
        raise Http404()

    invitation = get_object_or_404(Invitation, id=invitation_id)
    subject, message = invitation.generate_message(commit=False)
    data = {
        'subject': subject,
        'message': message
    }
    json_data = json.JSONEncoder(ensure_ascii=False).encode({
        'success': True,
        'data': data
    })
    return HttpResponse(json_data, mimetype='application/json')

@csrf_exempt
@login_required
def invitation_send(request, invitation_id):
    if not request.user.is_superuser:
        raise Http404()

    invitation = get_object_or_404(Invitation, id=invitation_id)
    invitation.send()
    json_data = json.JSONEncoder(ensure_ascii=False).encode({
        'success': True,
        'message': ''
    })
    return HttpResponse(json_data, mimetype='application/json')


@csrf_exempt
@login_required
def invitation_save(request):
    if not request.user.is_superuser:
        raise Http404
    if request.method == 'POST':
        invitation_id = request.REQUEST.get('id')
        fullname = request.REQUEST.get('fullname')
        email = request.REQUEST.get('email')
        radio_id = request.REQUEST.get('radio_id')
        subject = request.REQUEST.get('subject')
        message = request.REQUEST.get('message')

        invitation = get_object_or_404(Invitation, id=invitation_id)
        invitation.fullname = fullname
        invitation.email = email
        invitation.radio_id = radio_id
        invitation.subject = subject
        invitation.message = message
        invitation.save()

        json_data = json.JSONEncoder(ensure_ascii=False).encode({
            'success': True,
            'message': ''
        })
        return HttpResponse(json_data, mimetype='application/json')

    raise Http404


@csrf_exempt
@login_required
def yasound_songs(request, song_id=None):
    if not request.user.is_superuser:
        raise Http404()
    if request.method == 'GET':
        qs = YasoundSong.objects.all()
        yasound_song_id = request.REQUEST.get('id')
        name = request.REQUEST.get('name', '')
        artist_name = request.REQUEST.get('artist_name', '')
        album_name = request.REQUEST.get('album_name', '')

        if yasound_song_id:
            qs = qs.filter(id=yasound_song_id)
        if name:
            qs = qs.filter(name_simplified__istartswith=name)
        if artist_name:
            qs = qs.filter(artist_name_simplified__istartswith=artist_name)
        if album_name:
            qs = qs.filter(album_name_simplified__istartswith=album_name)

        grid = YasoundSongGrid()
        jsonr = yabackoffice_utils.generate_grid_rows_json(request, grid, qs)
        resp = utils.JsonResponse(jsonr)
        return resp
    raise Http404

@csrf_exempt
@login_required
def yasound_songs_find_metadata(request, song_id=None):
    if not request.user.is_superuser:
        raise Http404()

    ids = request.REQUEST.getlist('yasound_song_id')
    yasound_songs = YasoundSong.objects.filter(id__in=ids)

    res = ''
    for song in yasound_songs:
        synonyms = song.find_synonyms()
        for synonym in synonyms:
            res = res + '%s : %s' % (song, synonym)
            break # only first synonym is displayed

    json_data = json.JSONEncoder(ensure_ascii=False).encode({
        'success': True,
        'data': res,
    })
    resp = utils.JsonResponse(json_data)
    return resp

@csrf_exempt
@login_required
def yasound_songs_replace_metadata(request, song_id=None):
    if not request.user.is_superuser:
        raise Http404()

    ids = request.REQUEST.getlist('yasound_song_id')
    yasound_songs = YasoundSong.objects.filter(id__in=ids)

    for song in yasound_songs:
        synonyms = song.find_synonyms()
        for synonym in synonyms:
            name = synonym.get('name', '')
            artist = synonym.get('artist', '')
            album = synonym.get('album', '')
            to_save=False
            if len(name) > 0:
                song.name = name
                song.name_simplified = get_simplified_name(name)
                to_save = True
            if len(artist) > 0:
                song.artist_name = artist
                song.artist_name_simplified = get_simplified_name(artist)
                to_save = True
            if len(album) > 0:
                song.album_name = album
                song.album_name_simplified = get_simplified_name(album)
                to_save = True

            if to_save:
                song.save()
                song.build_fuzzy_index(upsert=True)

            break # only first synonym is handled

    json_data = json.JSONEncoder(ensure_ascii=False).encode({
        'success': True,
    })
    resp = utils.JsonResponse(json_data)
    return resp

@csrf_exempt
@login_required
def rejected_songs(request):
    if not request.user.is_superuser:
        raise Http404()

    if request.method == 'GET':
        mm = MatchingErrorsManager()
        skip = int(request.REQUEST.get('start', 0))
        limit = int(request.REQUEST.get('limit', 25))

        docs = mm.all(skip=skip, limit=limit)

        data = []
        for doc in docs:
            yasound_song = YasoundSong.objects.get(id=doc.get('yasound_song_id'))
            reject_count = doc.get('reject_count')

            data.append({
                'id': yasound_song.id,
                'name': yasound_song.name,
                'artist_name': yasound_song.artist_name,
                'album_name': yasound_song.album_name,
                'reject_count': reject_count,
            })
        json_data = json.JSONEncoder(ensure_ascii=False).encode({
            'success': True,
            'data': data,
            'results': len(data)
        })
        resp = utils.JsonResponse(json_data)
        return resp
    raise Http404

@csrf_exempt
@login_required
def users(request, user_id=None):
    if not request.user.is_superuser:
        raise Http404()
    if request.method == 'GET':
        qs = UserProfile.objects.all()
        filters = ['name', 'facebook_uid',
                   'last_authentication_date',
                   ('email', 'user__email'),
                   ('date_joined', 'user__date_joined'),
                   ('is_active', 'user__is_active'),
                   ('is_superuser', 'user__is_superuser')]
        grid = UserProfileGrid()
        jsonr = yabackoffice_utils.generate_grid_rows_json(request, grid, qs, filters)
        resp = utils.JsonResponse(jsonr)
        return resp
    elif request.method == 'POST' and not user_id:
        action = request.REQUEST.get('action')
        if action == 'disable':
            ids = request.REQUEST.getlist('users_id')
            User.objects.filter(userprofile__id__in=ids).update(is_active=False)
        elif action == 'fake':
            ids = request.REQUEST.getlist('users_id')
            User.objects.filter(userprofile__id__in=ids).update(is_active=False)
            RadioUser.objects.filter(user__userprofile__id__in=ids).update(favorite=False)
            WallEvent.objects.filter(user__userprofile__id__in=ids).filter(type=yabase_settings.EVENT_LIKE).delete()

            radios = Radio.objects.filter(radiouser__user__userprofile__id__in=ids)
            for radio in radios:
                radio.fix_favorites()

            from emencia.django.newsletter.models import Contact
            users = User.objects.filter(userprofile__id__in=ids)
            for user in users:
                Contact.objects.filter(email=user.email).delete()

        elif action == 'enable':
            ids = request.REQUEST.getlist('users_id')
            User.objects.filter(userprofile__id__in=ids).update(is_active=True)
        elif action == 'enable_hd':
            ids = request.REQUEST.getlist('users_id')
            profiles = UserProfile.objects.filter(id__in=ids)
            for profile in profiles:
                profile.permissions.hd = True
                profile.save()
        elif action == 'disable_hd':
            ids = request.REQUEST.getlist('users_id')
            profiles = UserProfile.objects.filter(id__in=ids)
            for profile in profiles:
                profile.permissions.hd = False
                profile.save()
        elif action == 'export':
            ids = request.REQUEST.getlist('users_id')
            if len(ids) > 0 and len(ids[0]) > 0:
                qs = User.objects.filter(userprofile__id__in=ids)
            else:
                qs = User.objects.filter(is_active=True)
            data = account_export.export_excel(qs)

            response = HttpResponse(data, mimetype='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename=users.xls'
            return response
        json_data = json.JSONEncoder(ensure_ascii=False).encode({
            'success': True,
            'message': ''
        })
        return HttpResponse(json_data, mimetype='application/json')
    raise Http404

@login_required
def users_history(request):
    if not request.user.is_superuser:
        raise Http404()
    if request.method == 'GET':
        start = int(request.REQUEST.get('start', 0))
        limit = int(request.REQUEST.get('limit', 25))

        user_id = int(request.REQUEST.get('user_id', 0))
        uh = UserHistory()
        qs = []
        count = 0
        if user_id > 0:
            count = uh.all(user_id=user_id).count()
            qs = uh.all(user_id=user_id, start=start, limit=limit)
        data = []
        for doc in qs:
            user_name = doc.get('user_name')
            history_type = doc.get('type')
            details = doc.get('data', {})
            if not details:
                details = {}

            radio = details.get('radio_name', '')
            message = details.get('message', '')
            song = details.get('song_name', '')
            share_type = details.get('share_type', '')
            atype = details.get('atype', '')

            data.append({
                'username': user_name,
                'date': doc.get('date'),
                'type': history_type,
                'atype': atype,
                'message': message,
                'radio': unicode(radio),
                'song': unicode(song),
                'share_type': unicode(share_type)
            })
        json_data = MongoAwareEncoder(ensure_ascii=False).encode({
            'success': True,
            'data': data,
            'results': count
        })
        resp = utils.JsonResponse(json_data)
        return resp

    raise Http404

@csrf_exempt
@login_required
def wall_events(request, wall_event_id=None):
    if not request.user.is_superuser:
        raise Http404()
    if request.method == 'GET':
        qs = WallEvent.objects.filter(type=yabase_settings.EVENT_MESSAGE)
        filters = ['user_name',
                   ('user_id', 'user__userprofile__id', 'exact'),
                   ('radio_id', 'radio__id', 'exact'),
                   'text']
        grid = WallEventGrid()
        jsonr = yabackoffice_utils.generate_grid_rows_json(request, grid, qs, filters)
        resp = utils.JsonResponse(jsonr)
        return resp
    elif request.method == 'DELETE':
        we = get_object_or_404(WallEvent, id=wall_event_id)
        we.delete()
        data = {"success":True,"message":"ok","data":[]}
        resp = utils.JsonResponse(json.JSONEncoder(ensure_ascii=False).encode(data))
        return resp
    raise Http404


@csrf_exempt
@login_required
def radios_stats_created(request):
    if not request.user.is_superuser:
        raise Http404()

    data = []
    for i in range(1, 10):
        data.append({
            'timestamp': 'timestamp%d' %(i),
            'created_radios': i*100
        })
    json_data = json.JSONEncoder(ensure_ascii=False).encode({
        'success': True,
        'data': data,
        'results': len(data)
    })
    resp = utils.JsonResponse(json_data)
    return resp

@csrf_exempt
@login_required
def keyfigures(request, template_name='yabackoffice/keyfigures.html'):
    if not request.user.is_superuser:
        raise Http404()

    overall_listening_time = Radio.objects.all().aggregate(Sum('overall_listening_time'))['overall_listening_time__sum']
    try:
        overall_listening_time_str = datetime.timedelta(seconds=overall_listening_time)
    except:
        overall_listening_time_str = _('Unavailable')

    total_friend_count = cache.get('total_friend_count')
    if total_friend_count is None:
        total_friend_count = _('Unavailable')

    facebook_user_count = UserProfile.objects.exclude(facebook_token='').count()
    twitter_user_count = UserProfile.objects.exclude(twitter_token='').count()
    yasound_user_count = UserProfile.objects.exclude(yasound_email='').count()

    confirmed_emails = EmailAddress.objects.filter(verified=True).count()
    email_address_count = EmailAddress.objects.all().count()
    not_confirmed_emails = EmailAddress.objects.filter(verified=False).count()
    confirmed_emails_ratio = '%.2f' % ( 100 * float(confirmed_emails) / float(email_address_count) )

    device_notifications_activated = Device.objects.filter(ios_token__gt=0).count()

    song_metadata_count = SongMetadata.objects.all().count()
    unmatched_song_metadata_count = SongMetadata.objects.filter(yasound_song_id__isnull=True).count()
    matched_songs_ratio = '%.2f' % (100-(100*float(unmatched_song_metadata_count)/float(song_metadata_count)))

    ready_radio_count = Radio.objects.filter(ready=True).count()
    total_radio = Radio.objects.all().count()

    ready_radio_ratio = '%.2f' %  ( 100 * float(ready_radio_count) / float(total_radio) )

    try:
        r = requests.get('http://yas-web-08.ig-1.net:8000/ping')
        streamer_status = r.text
    except:
        streamer_status = _('Unavailable')

    um = UserMetricsManager()
    messages_per_user = um.calculate_messages_per_user_mean()
    likes_per_user = um.calculate_likes_per_user_mean()

    email_count = User.objects.filter(email__contains='@', is_active=True).count()
    newsletter_subscribers = Contact.objects.filter(subscriber=True).count()

    return render_to_response(template_name, {
        "user_count": User.objects.filter(is_active=True).count(),
        "ready_radio_count": ready_radio_count,
        "ready_radio_ratio" : ready_radio_ratio,
        "wall_message_count": WallEvent.objects.filter(type=yabase_settings.EVENT_MESSAGE).count(),
        "wall_like_count": WallEvent.objects.filter(type=yabase_settings.EVENT_LIKE).count(),
        "favorite_count": RadioUser.objects.filter(favorite=True).count(),
        "yasound_friend_count": UserProfile.objects.all().aggregate(Count('friends'))['friends__count'],
        "listening_time": overall_listening_time_str,
        "uploaded_song_count" : YasoundSong.objects.filter(id__gt=2059600).count(),
        "total_friend_count": total_friend_count,
        "facebook_user_count": facebook_user_count,
        "twitter_user_count": twitter_user_count,
        "yasound_user_count": yasound_user_count,
        "streamer_status": streamer_status,
        "song_metadata_count": song_metadata_count,
        "unmatched_song_metadata_count": unmatched_song_metadata_count,
        "matched_songs_ratio": matched_songs_ratio,
        "device_notifications_activated" : device_notifications_activated,
        "confirmed_emails" : confirmed_emails,
        "not_confirmed_emails": not_confirmed_emails,
        "email_address_count": email_address_count,
        "confirmed_emails_ratio": confirmed_emails_ratio,
        "messages_per_user": messages_per_user,
        "likes_per_user": likes_per_user,
        "email_count": email_count,
        "newsletter_subscribers": newsletter_subscribers,
    }, context_instance=RequestContext(request))

@csrf_exempt
@login_required
def radio_tags(request, template_name='yabackoffice/radio_tags.html'):
    if not request.user.is_superuser:
        raise Http404()

    return render_to_response(template_name, {
    }, context_instance=RequestContext(request))

def _format_metrics(metrics):
    for metric in metrics:
        if 'listening_time' in metric:
            if 'listening_count' in metric:
                try:
                    listening_time = float(metric['listening_time'])
                    listening_count = float(metric['listening_count'])

                    average_duration = listening_time / listening_count
                    formatted_time = datetime.timedelta(seconds=int(average_duration))

                    metric['average_duration'] = formatted_time
                except:
                    pass

            try:
                formatted_time = datetime.timedelta(seconds=int(metric['listening_time']))
                metric['listening_time'] = formatted_time
            except:
                pass

    return metrics

@csrf_exempt
@login_required
def metrics(request, template_name='yabackoffice/metrics.html'):
    if not request.user.is_superuser:
        raise Http404()

    mm = GlobalMetricsManager()
    metrics = mm.get_current_metrics()
    _format_metrics(metrics)

    return render_to_response(template_name, {
        "metrics": metrics,
    }, context_instance=RequestContext(request))

def _metric_label(code):
    if code == 'new_users':
        return _('New users')
    elif code == 'new_radios':
        return _('New radios')
    elif code == 'new_real_radios':
        return _('New real radios')
    elif code == 'deleted_radios':
        return _('Deleted radios')
    elif code == 'new_listeners':
        return _('Number of people who have already listened to at least one radio')
    elif code == 'listening_time':
        return _('Listening time')
    elif code == 'average_duration':
        return _('Average duration')
    elif code == 'device_notifications_activated':
        return _('Notifications activated on device')
    elif code == 'device_notifications_disabled':
        return _('Notifications disabled on device')
    elif code == 'device_count':
        return _('Device count')
    elif code == 'new_wall_messages':
        return _('Wall messages')
    elif code == 'new_song_like':
        return _('Song likes')
    elif code == 'new_radio_like':
        return _('Radio likes')
    elif code == 'new_radio_dislike':
        return _('Radio dislikes')
    elif code == 'new_radio_neutral':
        return _('Radio neutral')
    elif code == 'new_favorite_radio':
        return _('Radio favorites')
    elif code == 'new_not_favorite_radio':
        return _('Radio unfavorites')
    elif code == 'new_animator_activity':
        return _('Animator actions')
    elif code == 'new_share':
        return _('New shares')
    elif code == 'new_moderator_abuse_msg_activity':
        return _('Abuse report')
    elif code == 'new_share_facebook':
        return _('Facebook share')
    elif code == 'new_share_twitter':
        return _('Twitter share')
    elif code == 'new_share_email':
        return _('Email share')
    return code

def _export_metrics(metrics):
    wb = xlwt.Workbook()

    ws = wb.add_sheet(unicode(_('Metrics')))
    line, col = 0, 0

    greyBG = xlwt.Pattern()
    greyBG.pattern = greyBG.SOLID_PATTERN
    greyBG.pattern_fore_colour = 3

    greyFontStyle = xlwt.XFStyle()
    greyFontStyle.pattern = greyBG
    # header line
    headerBG = xlwt.easyxf('pattern: pattern solid, fore_colour yellow;')
    ws.write(line, col, unicode(_('metric')), headerBG)
    for i, metric in enumerate(metrics):
        ws.write(line, col + 1 + i, metric.get('timestamp'), headerBG)


    line, col = 1, 0
    keys = [
        'new_users',
        'new_radios',
        'new_real_radios',
        'deleted_radios',
        'new_listeners',
        'listening_time',
        'average_duration',
        'device_notifications_activated',
        'device_notifications_disabled',
        'device_count',
        'new_wall_messages',
        'new_song_like',
        'new_favorite_radio',
        'new_not_favorite_radio',
        'new_animator_activity',
        'new_share',
        'new_share_facebook',
        'new_share_twitter',
        'new_share_email',
    ]
    for key in keys:
        ws.write(line, col, unicode(_metric_label(key)))

        for i, metric in enumerate(metrics):
            value = unicode(metric.get(key, ''))
            ws.write(line, col+1+i, value)

        line = line+1

    output = StringIO.StringIO()
    wb.save(output)
    content = output.getvalue()
    output.close()
    return content

@csrf_exempt
@login_required
def metrics_export(request, template_name='yabackoffice/metrics.html'):
    if not request.user.is_superuser:
        raise Http404()

    mm = GlobalMetricsManager()
    metrics = mm.get_current_metrics()
    _format_metrics(metrics)

    data = _export_metrics(metrics)
    response = HttpResponse(data, mimetype='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename=metrics.xls'
    return response



@csrf_exempt
@login_required
def past_month_metrics(request, template_name='yabackoffice/metrics.html'):
    if not request.user.is_superuser:
        raise Http404()

    mm = GlobalMetricsManager()
    metrics = mm.get_past_month_metrics()
    _format_metrics(metrics)

    return render_to_response(template_name, {
        "metrics": metrics,
    }, context_instance=RequestContext(request))

@csrf_exempt
@login_required
def past_month_metrics_export(request, template_name='yabackoffice/metrics.html'):
    if not request.user.is_superuser:
        raise Http404()

    mm = GlobalMetricsManager()
    metrics = mm.get_past_month_metrics()
    _format_metrics(metrics)

    data = _export_metrics(metrics)
    response = HttpResponse(data, mimetype='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename=metrics.xls'
    return response

@csrf_exempt
@login_required
def past_year_metrics(request, template_name='yabackoffice/metrics.html'):
    if not request.user.is_superuser:
        raise Http404()

    mm = GlobalMetricsManager()
    metrics = mm.get_past_year_metrics()
    _format_metrics(metrics)

    return render_to_response(template_name, {
        "metrics": metrics,
    }, context_instance=RequestContext(request))

@csrf_exempt
@login_required
def past_year_metrics_export(request, template_name='yabackoffice/metrics.html'):
    if not request.user.is_superuser:
        raise Http404()

    mm = GlobalMetricsManager()
    metrics = mm.get_past_year_metrics()
    _format_metrics(metrics)

    data = _export_metrics(metrics)
    response = HttpResponse(data, mimetype='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename=past_year_metrics.xls'
    return response

@csrf_exempt
def light_metrics(request, template_name='yabackoffice/light_metrics.html'):
    user_count = User.objects.all().count()
    overall_listening_time = Radio.objects.all().aggregate(Sum('overall_listening_time'))['overall_listening_time__sum']
    try:
        overall_listening_time_str = datetime.timedelta(seconds=overall_listening_time)
    except:
        overall_listening_time_str = _('Unavailable')

    return render_to_response(template_name, {
        'user_count': user_count,
        "ready_radio_count": Radio.objects.filter(ready=True).count(),
        "listening_time": unicode(overall_listening_time_str),
        "wall_message_count": WallEvent.objects.filter(type=yabase_settings.EVENT_MESSAGE).count(),
    }, context_instance=RequestContext(request))


@csrf_exempt
@login_required
def songmetadata_top_missing(request):
    if not request.user.is_superuser:
        raise Http404

    if request.method == 'GET':
        tm =TopMissingSongsManager()
        qs = tm.all()
        data = []
        for metadata in qs:
            if SongMetadata.objects.filter(id=metadata['db_id'], yasound_song_id__isnull=False).count() == 0:
                data.append({
                    'id': metadata['db_id'],
                    'name': metadata['name'],
                    'artist_name': metadata['artist_name'],
                    'album_name': metadata['album_name'],
                    'songinstance__count': metadata['songinstance__count']
                })
        response = {
            'data': data,
            'results': qs.count(),
            'success': True
        }
        resp = utils.JsonResponse(json.dumps(response))
        return resp

    raise Http404

@csrf_exempt
@login_required
def songmetadata_most_popular(request):
    if not request.user.is_superuser:
        raise Http404

    if request.method == 'GET':
        start = int(request.REQUEST.get('start', 0))
        limit = int(request.REQUEST.get('limit', 25))

        mm = MostPopularSongsManager()
        qs = mm.all(start, limit)
        data = []
        for metadata in qs:
            data.append({
                'id': metadata['db_id'],
                'name': metadata['name'],
                'artist_name': metadata['artist'],
                'album_name': metadata['album'],
                'songinstance__count': metadata['songinstance__count']
            })
        response = {
            'data': data,
            'results': qs.count(),
            'success': True
        }
        resp = utils.JsonResponse(json.dumps(response))
        return resp

    raise Http404

@csrf_exempt
@login_required
def songmetadata_export_most_popular(request):
    if not request.user.is_superuser:
        raise Http404

    mm = MostPopularSongsManager()
    qs = mm.all(start=0, limit=16000)
    data = export_pur(qs)

    response = HttpResponse(data, mimetype='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename=songs.xls'
    return response

def _compare_metrics(m1, m2):
    order = [
        TimedMetricsManager.SLOT_24H,
        TimedMetricsManager.SLOT_3D,
        TimedMetricsManager.SLOT_7D,
        TimedMetricsManager.SLOT_15D,
        TimedMetricsManager.SLOT_30D,
        TimedMetricsManager.SLOT_90D,
        TimedMetricsManager.SLOT_90D_MORE,
    ]
    order1 = order.index(m1.get('timestamp'))
    order2 = order.index(m2.get('timestamp'))
    return cmp(order1, order2)

@csrf_exempt
@login_required
def metrics_graph_animators(request):
    if not request.user.is_superuser:
        raise Http404()

    tm = TimedMetricsManager()
    metrics = tm.all()
    data = []
    for metric in metrics:
        data.append({
            'timestamp': metric['type'],
            'animator_activity': metric['animator_activity'] if 'animator_activity' in metric else 0
        })

    data.sort(cmp=_compare_metrics)

    json_data = json.JSONEncoder(ensure_ascii=False).encode({
        'success': True,
        'data': data,
        'results': len(data)
    })
    resp = utils.JsonResponse(json_data)
    return resp


@csrf_exempt
@login_required
def metrics_graph_posts(request):
    if not request.user.is_superuser:
        raise Http404()

    um  = UserMetricsManager()
    metrics = um.messages_stats()
    data = []
    for metric in metrics:
        data.append({
            'message_count': metric['_id'],
            'user_count': metric['value']
        })

    json_data = json.JSONEncoder(ensure_ascii=False).encode({
        'success': True,
        'data': data,
        'results': len(data)
    })
    resp = utils.JsonResponse(json_data)
    return resp

@csrf_exempt
@login_required
def metrics_graph_likes(request):
    if not request.user.is_superuser:
        raise Http404()

    um  = UserMetricsManager()
    metrics = um.likes_stats()
    data = []
    for metric in metrics:
        data.append({
            'like_count': metric['_id'],
            'user_count': metric['value']
        })
    json_data = json.JSONEncoder(ensure_ascii=False).encode({
        'success': True,
        'data': data,
        'results': len(data)
    })
    resp = utils.JsonResponse(json_data)
    return resp

@csrf_exempt
@login_required
def metrics_graph_listen(request):
    if not request.user.is_superuser:
        raise Http404()

    tm = TimedMetricsManager()
    metrics = tm.all()
    data = []
    for metric in metrics:
        data.append({
            'timestamp': metric['type'],
            'listen_activity': metric['listen_activity'] if 'listen_activity' in metric else 0
        })
    data.sort(cmp=_compare_metrics)
    json_data = json.JSONEncoder(ensure_ascii=False).encode({
        'success': True,
        'data': data,
        'results': len(data)
    })
    resp = utils.JsonResponse(json_data)
    return resp

@csrf_exempt
@login_required
def metrics_graph_shares(request):
    if not request.user.is_superuser:
        raise Http404()

    tm = TimedMetricsManager()
    metrics = tm.all()
    data = []
    for metric in metrics:
        data.append({
            'timestamp': metric['type'],
            'share_activity': metric['share_activity'] if 'share_activity' in metric else 0,
            'share_facebook_activity': metric['share_facebook_activity'] if 'share_facebook_activity' in metric else 0,
            'share_twitter_activity': metric['share_twitter_activity'] if 'share_twitter_activity' in metric else 0,
            'share_email_activity': metric['share_email_activity'] if 'share_email_activity' in metric else 0,
        })
    data.sort(cmp=_compare_metrics)
    json_data = json.JSONEncoder(ensure_ascii=False).encode({
        'success': True,
        'data': data,
        'results': len(data)
    })
    resp = utils.JsonResponse(json_data)
    return resp


@login_required
def radio_activity_score_factors(request, coeff_id=None):
    if not request.user.is_superuser:
        raise Http404()

    from yametrics.models import RadioPopularityManager
    manager = RadioPopularityManager()

    if request.method == 'GET':
        coeffs = manager.coeff_documents()
        data = []
        for i in coeffs:
            data.append({
                         '_id': i['_id'],
                         'name': i['name'],
                         'value': i['value']
                         })

        json_data = MongoAwareEncoder(ensure_ascii=False).encode({
            'success': True,
            'data': data,
            'results': len(data)
        })
        resp = utils.JsonResponse(json_data)
        return resp
    elif request.method == 'PUT' and coeff_id is not None:
        coerce_put_post(request)
        data = request.REQUEST.get('data')
        decoded_data = json.loads(data)
        manager.update_coeff_doc(coeff_id, decoded_data)

        res = {"success":True}
        resp = utils.JsonResponse(json.JSONEncoder(ensure_ascii=False).encode(res))
        return utils.JsonResponse(resp)

    res = {"success":False}
    resp = utils.JsonResponse(json.JSONEncoder(ensure_ascii=False).encode(res))
    return utils.JsonResponse(resp)


@csrf_exempt
@login_required
def find_musicbrainz_id(request):
    ids = request.REQUEST.getlist('ids')
    for yasound_song in ids:
        task.find_musicbrainz_id.delay(yasound_song)
    json_data = json.JSONEncoder(ensure_ascii=False).encode({
        'success': True,
        'message': ''
    })
    return HttpResponse(json_data, mimetype='application/json')

@csrf_exempt
@login_required
def abuse_notifications(request):
    if not request.user.is_superuser:
        raise Http404()
    manager = AbuseManager()
    abuse_notifications = manager.all()
    data = []
    for notification in abuse_notifications:
        radio = Radio.objects.get(id=notification.get('radio'))
        sender = User.objects.get(id=notification.get('sender'))
        user_id = notification.get('user')
        if not user_id:
            wall_event_id = notification.get('db_id')
            try:
                we = WallEvent.objects.get(id=wall_event_id)
                user = we.user
            except WallEvent.DoesNotExist:
                continue
        else:
            user = User.objects.get(id=notification.get('user'))

        data.append({
            '_id': notification.get('_id'),
            'date': notification.get('date'),
            'sender': unicode(sender.get_profile()),
            'radio': unicode(radio),
            'user': unicode(user.get_profile()),
            'text': notification.get('text'),
        })
    json_data = json.dumps({
        'success': True,
        'data': data,
        'results': len(data)
    }, cls=MongoAwareEncoder)
    resp = utils.JsonResponse(json_data)
    return resp

@csrf_exempt
@login_required
def delete_abuse_notification(request):
    if not request.user.is_superuser:
        raise Http404()
    ids = request.REQUEST.getlist('notifications')
    manager = AbuseManager()
    for id in ids:
        doc = manager.get(id)
        try:
            we = WallEvent.objects.get(id=doc.get('db_id'))
            we.delete()
        except WallEvent.DoesNotExist:
            pass
        manager.delete(id)

    data = {"success":True,"message":"ok","data":[]}
    resp = utils.JsonResponse(json.JSONEncoder(ensure_ascii=False).encode(data))
    return resp

@csrf_exempt
@login_required
def ignore_abuse_notification(request):
    if not request.user.is_superuser:
        raise Http404()
    ids = request.REQUEST.getlist('notifications')
    manager = AbuseManager()
    for id in ids:
        manager.delete(id)

    data = {"success":True,"message":"ok","data":[]}
    resp = utils.JsonResponse(json.JSONEncoder(ensure_ascii=False).encode(data))
    return resp


@csrf_exempt
@login_required
def premium_non_unique_promocodes(request):
    if not request.user.is_superuser:
        raise Http404()

    if request.method == 'GET':
        qs = Promocode.objects.filter(unique=False)
        grid = PromocodeGrid()
        filters = [
            'code'
        ]
        jsonr = yabackoffice_utils.generate_grid_rows_json(request, grid, qs, filters)
        resp = utils.JsonResponse(jsonr)
        return resp
    elif request.method == 'POST':
        service_id = request.REQUEST.get('service_id')
        duration = request.REQUEST.get('duration', 1)
        duration_unit = request.REQUEST.get('duration_unit', 0)
        group_name = request.REQUEST.get('group', '')
        code = request.REQUEST.get('code')
        group = None;
        if group_name != '':
            group, created = PromocodeGroup.objects.get_or_create(name=group_name)

        Promocode.objects.create(service=Service.objects.get(id=service_id),
            duration=duration,
            duration_unit=duration_unit,
            code=code,
            group=group,
            enabled=True,
            unique=False)
        data = {"success":True,"message":"ok"}
        resp = utils.JsonResponse(json.JSONEncoder(ensure_ascii=False).encode(data))
        return resp
    raise Http404

@csrf_exempt
@login_required
def premium_unique_promocodes(request):
    if not request.user.is_superuser:
        raise Http404()

    if request.method == 'GET':
        qs = Promocode.objects.filter(unique=True, enabled=True)
        grid = PromocodeGrid()
        filters = [
            'code'
        ]
        jsonr = yabackoffice_utils.generate_grid_rows_json(request, grid, qs, filters)
        resp = utils.JsonResponse(jsonr)
        return resp
    elif request.method == 'POST':
        service_id = request.REQUEST.get('service_id')
        duration = request.REQUEST.get('duration', 1)
        duration_unit = request.REQUEST.get('duration_unit', 0)
        prefix = request.REQUEST.get('prefix', 'YA-')
        group_name = request.REQUEST.get('group', '')
        count = int(request.REQUEST.get('count', 50))
        group = None;
        if group_name != '':
            group, created = PromocodeGroup.objects.get_or_create(name=group_name)

        Promocode.objects.generate_unique_codes(service=Service.objects.get(id=service_id),
            duration=duration,
            duration_unit=duration_unit,
            group=group,
            prefix=prefix,
            count=count)
        data = {"success":True,"message":"ok"}
        resp = utils.JsonResponse(json.JSONEncoder(ensure_ascii=False).encode(data))
        return resp

    raise Http404

@csrf_exempt
@login_required
def premium_promocodes(request, promocode_id=None):
    if not request.user.is_superuser:
        raise Http404()

    if request.method == 'PUT' and promocode_id is not None:
        coerce_put_post(request)
        promocode = get_object_or_404(Promocode, id=promocode_id)
        service_id = request.REQUEST.get('service_id')
        duration = request.REQUEST.get('duration', 1)
        duration_unit = request.REQUEST.get('duration_unit', 0)
        code = request.REQUEST.get('code')
        group_name = request.REQUEST.get('group', '')
        enabled = request.REQUEST.get('enabled')
        service = get_object_or_404(Service, id=service_id)

        group = None;
        if group_name != '':
            group, created = PromocodeGroup.objects.get_or_create(name=group_name)

        promocode.code = code
        promocode.service = service
        promocode.duration = duration
        promocode.duration_unit = duration_unit
        promocode.group = group
        if enabled == 'true':
            promocode.enabled = True
        else:
            promocode.enabled = False

        promocode.save()
        data = {"success":True,"message":"ok"}
        resp = utils.JsonResponse(json.JSONEncoder(ensure_ascii=False).encode(data))
        return resp
    elif request.method == 'POST':
        action = request.REQUEST.get('action')
        if action == 'delete':
            promocode_ids = request.REQUEST.getlist('promocode_id')
            Promocode.objects.filter(id__in=promocode_ids).update(enabled=False)

            data = {"success":True,"message":"ok"}
            resp = utils.JsonResponse(json.JSONEncoder(ensure_ascii=False).encode(data))
            return resp
        elif action == 'export':
            promocode_ids = request.REQUEST.get('promocode_id', [])
            qs = Promocode.objects.filter(id__in=promocode_ids.split(','))
            data = yapremium_export.export_promocodes_excel(qs)

            response = HttpResponse(data, mimetype='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename=promocodes.xls'
            return response
        elif action == 'export_group':
            group_name = request.REQUEST.get('group')
            group = get_object_or_404(PromocodeGroup, name=group_name)
            qs = Promocode.objects.filter(group=group)
            data = yapremium_export.export_promocodes_excel(qs)

            response = HttpResponse(data, mimetype='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename=promocodes-%s.xls' % (group.name)
            return response
    raise Http404

@csrf_exempt
@login_required
def geoperm_countries(request, country_id=None):
    if not request.user.is_superuser:
        raise Http404()

    if request.method == 'GET':
        qs = Country.objects.all().order_by('code')
        grid = CountryGrid()
        filters = [
            'code',
            'name'
        ]
        jsonr = yabackoffice_utils.generate_grid_rows_json(request, grid, qs, filters)
        resp = utils.JsonResponse(jsonr)
        return resp
    elif request.method == 'POST':
        action = request.REQUEST.get('action')
        if action == 'delete':
            country_ids = request.REQUEST.getlist('country_id')
            Country.objects.filter(id__in=country_ids).delete()
            data = {"success":True,"message":"ok"}
            resp = utils.JsonResponse(json.JSONEncoder(ensure_ascii=False).encode(data))
            return resp
        else:
            name = request.REQUEST.get('name')
            code = request.REQUEST.get('code')
            try:
                Country.objects.create(name=name, code=code)
                data = {"success":True,"message":"ok"}
            except IntegrityError:
                data = {"success":False,"message":unicode(_('This country already exists'))}
            resp = utils.JsonResponse(json.JSONEncoder(ensure_ascii=False).encode(data))
            return resp
    elif request.method == 'PUT' and country_id is not None:
        coerce_put_post(request)
        country = get_object_or_404(Country, id=country_id)
        name = request.REQUEST.get('name')
        code = request.REQUEST.get('code')
        country.name = name
        country.code = code
        try:
            country.save()
            data = {"success":True,"message":"ok"}
        except IntegrityError:
            data = {"success":False,"message":unicode(_('This country already exists'))}
        resp = utils.JsonResponse(json.JSONEncoder(ensure_ascii=False).encode(data))
        return resp
    raise Http404

@csrf_exempt
@login_required
def geoperm_countries_features(request, country_id, geofeature_id=None):
    if not request.user.is_superuser:
        raise Http404()

    if request.method == 'GET':
        qs = GeoFeature.objects.filter(country__id=country_id).order_by('feature')
        grid = GeoFeatureGrid()
        jsonr = yabackoffice_utils.generate_grid_rows_json(request, grid, qs)
        resp = utils.JsonResponse(jsonr)
        return resp
    elif request.method == 'POST':
        action = request.REQUEST.get('action')
        if action == 'delete':
            geofeature_ids = request.REQUEST.getlist('geofeature_id')
            GeoFeature.objects.filter(id__in=geofeature_ids).delete()
            data = {"success":True,"message":"ok"}
            resp = utils.JsonResponse(json.JSONEncoder(ensure_ascii=False).encode(data))
            return resp
        else:
            feature = request.REQUEST.get('feature')
            try:
                GeoFeature.objects.create(feature=feature, country=Country.objects.get(id=country_id))
                data = {"success":True,"message":"ok"}
            except IntegrityError:
                data = {"success":False,"message":unicode(_('This feature already exists'))}
            resp = utils.JsonResponse(json.JSONEncoder(ensure_ascii=False).encode(data))
            return resp
    elif request.method == 'PUT' and geofeature_id is not None:
        coerce_put_post(request)
        geofeature = get_object_or_404(GeoFeature, id=geofeature_id)
        feature = request.REQUEST.get('feature')
        geofeature.feature = feature
        try:
            geofeature.save()
            data = {"success":True,"message":"ok"}
        except IntegrityError:
            data = {"success":False,"message":unicode(_('This feature already exists'))}

        resp = utils.JsonResponse(json.JSONEncoder(ensure_ascii=False).encode(data))
        return resp
    raise Http404
