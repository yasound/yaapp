from django.conf import settings
from django.contrib.auth.models import User
from redis import Redis
from yacore.api import MongoAwareEncoder
import json
import logging
import signals as yamessage_signals

logger = logging.getLogger("yaapp.yabase")


def new_notification_handler(sender, notification, **kwargs):
    red = Redis(host=settings.PUSH_REDIS_HOST, db=settings.PUSH_REDIS_DB)
    
    recipient = notification['dest_user_id']
    if recipient is None:
        return
    
    user = User.objects.get(id=recipient)
    
    from yamessage.models import NotificationsManager
    nm = NotificationsManager()
    
    unread_count = nm.unread_count(user.id)
    notification['unread_count'] = unread_count
    channel = 'user.%s' % (user.id)
    logger.info("publishing message to %s" % (channel)) 
    
    data = {
        'event_type': 'notification',
        'data': json.dumps(notification, cls=MongoAwareEncoder),
    }
    json_data = json.JSONEncoder(ensure_ascii=False).encode(data)
    red.publish(channel, json_data)
    
def unread_changed_handler(sender, dest_user_id, count, **kwargs):
    red = Redis(host=settings.PUSH_REDIS_HOST, db=settings.PUSH_REDIS_DB)
    user = User.objects.get(id=dest_user_id)

    
    channel = 'user.%s' % (user.id)
    logger.info("publishing message to %s" % (channel)) 
    
    data = {
        'count': count
    }
    
    data = {
        'event_type': 'notification_unread_count',
        'data': json.dumps(data, cls=MongoAwareEncoder),
    }
    json_data = json.JSONEncoder(ensure_ascii=False).encode(data)
    red.publish(channel, json_data)
    
def install_handlers():
    yamessage_signals.new_notification.connect(new_notification_handler)
    yamessage_signals.unread_changed.connect(unread_changed_handler)
