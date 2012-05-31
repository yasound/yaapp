from django.conf import settings
from django.contrib.auth.models import User
from redis import Redis
from yacore.json import MongoAwareEncoder
import json
import logging
import signals as yamessage_signals

logger = logging.getLogger("yaapp.yabase")


def new_notification_handler(sender, notification, **kwargs):
    red = Redis(host=settings.PUSH_REDIS_HOST, db=settings.PUSH_REDIS_DB)
    
    recipient = notification['dest_user_id']
    if recipient is None:
        return
    
    user = User.objects.get(userprofile__id=recipient)
    
    channel = 'user.%s' % (user.id)
    logger.info("publishing message to %s" % (channel)) 
    
    data = {
        'event_type': 'notification',
        'data': json.dumps(notification, cls=MongoAwareEncoder)
    }
    json_data = json.JSONEncoder(ensure_ascii=False).encode(data)
    red.publish(channel, json_data)
    
def install_handlers():
    yamessage_signals.new_notification.connect(new_notification_handler)
