from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.conf import settings
from models import WallManager
from yacore.decorators import check_api_key
from yacore.api import api_response
from yabase.models import Radio
from yabase import signals as yabase_signals
from emailconfirmation.models import EmailTemplate
from django.core.mail import send_mail
import json


@check_api_key(methods=['GET', 'DELETE'], login_required=False)
def wall(request, radio_uuid, event_id=None):
    wm = WallManager()
    if request.method == 'GET':
        offset = int(request.REQUEST.get('offset', 0))
        try:
            limit = int(request.REQUEST.get('limit', 20))
        except:
            limit = 20
        total_count = wm.events_count_for_radio(radio_uuid)
        data = wm.events_for_radio(radio_uuid, skip=offset, limit=limit)
        return api_response(list(data), total_count=total_count, limit=limit, offset=offset)
    elif request.method == 'DELETE':
        radio = get_object_or_404(Radio, uuid=radio_uuid)
        if not request.user.is_superuser and (radio.creator != request.user):
            return HttpResponse(status=401)

        wm.remove_event(event_id)
        yabase_signals.new_moderator_del_msg_activity.send(sender=request.user, user=request.user)

        response = {'success': True}
        res = json.dumps(response)
        return HttpResponse(res)


@csrf_exempt
@check_api_key(methods=['POST'])
def report_event_as_abuse(request, event_id):
    wm = WallManager()
    event = wm.event(event_id)
    if event is None:
        raise Http404

    wm.mark_as_abuse(event_id)

    context = {
        "user": request.user,
        "message": {
            'text': event.get('message').get('text'),
            'user': User.objects.get(username=event.get('message').get('username')),
            'id': event.get('event_id')
        },
    }
    subject, message = EmailTemplate.objects.generate_mail(EmailTemplate.EMAIL_TYPE_ABUSE, context)
    subject = "".join(subject.splitlines())
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [a[1] for a in settings.MODERATORS])

    response = {'success': True}
    res = json.dumps(response)
    return HttpResponse(res)
