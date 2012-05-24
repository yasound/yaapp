from account.models import UserProfile, Device
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
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
from extjs import utils
from grids import SongInstanceGrid, RadioGrid, InvitationGrid, YasoundSongGrid
from yabackoffice.forms import RadioForm, InvitationForm
from yabackoffice.grids import UserProfileGrid, WallEventGrid
from yabackoffice.models import BackofficeRadio
from yabase import settings as yabase_settings
from yabase.models import Radio, SongInstance, WallEvent, RadioUser, \
    SongMetadata
from yainvitation.models import Invitation
from yametrics.models import GlobalMetricsManager, TopMissingSongsManager,\
    TimedMetricsManager
from yaref.models import YasoundSong
import datetime
import requests
import simplejson as json
import utils as yabackoffice_utils

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
        radio.delete()
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
        if action == 'fake':
            ids = request.REQUEST.getlist('users_id')
            User.objects.filter(userprofile__id__in=ids).update(is_active=False)
            RadioUser.objects.filter(user__userprofile__id__in=ids).update(favorite=False)
            WallEvent.objects.filter(user__userprofile__id__in=ids).filter(type=yabase_settings.EVENT_LIKE).delete()

            radios = Radio.objects.filter(radiouser__user__userprofile__id__in=ids)
            for radio in radios:
                radio.fix_favorites()

        elif action == 'enable':
            ids = request.REQUEST.getlist('users_id')
            User.objects.filter(userprofile__id__in=ids).update(is_active=True)
        json_data = json.JSONEncoder(ensure_ascii=False).encode({
            'success': True,
            'message': ''
        })
        return HttpResponse(json_data, mimetype='application/json')
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
        r = requests.get('http://yas-web-01.ig-1.net:8000/ping')    
        streamer_status = r.text
    except:
        streamer_status = _('Unavailable')
        
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
        "confirmed_emails_ratio": confirmed_emails_ratio
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
    json_data = json.JSONEncoder(ensure_ascii=False).encode({
        'success': True,
        'data': data,
        'results': len(data)
    })
    resp = utils.JsonResponse(json_data)
    return resp