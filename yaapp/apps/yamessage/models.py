from bson.objectid import ObjectId
from django.conf import settings
from pymongo import DESCENDING
import datetime
import settings as yamessage_settings
import signals as yamessage_signals
from django.contrib.auth.models import User
from yabase.models import Radio

if settings.ENABLE_PUSH:
    from push import install_handlers
    install_handlers()

class NotificationsManager():
    
    def __init__(self):
        self.db = settings.MONGO_DB
        self.notifications = self.db.notifications
        self.notifications.ensure_index("date")
        self.notifications.ensure_index("dest_user_id")
        
    def add_notification(self, recipient_user_id, notif_type, params=None, from_user_id=None, from_radio_id=None):
        if settings.YAMESSAGE_NOTIFICATION_MANAGER_ENABLED == False:
            print 'NotificationManager is disabled (settings.YAMESSAGE_NOTIFICATION_MANAGER_ENABLED = False)'
            return;
        from_user_name = None
        if from_user_id is not None:
            try:
                u = User.objects.get(id=from_user_id)
                from_user_name = u.userprofile.name
            except User.DoesNotExist:
                pass 
        from_radio_name = None
        if from_radio_id is not None:
            try:
                r = Radio.objects.get(id=from_radio_id)
                from_radio_name = r.name
            except Radio.DoesNotExist:
                pass
        text = self.text_for_notification(notif_type, params)
        d = datetime.datetime.now()
        notif = {'type':notif_type,
                 'text':text,
                 'date':d,
                 'dest_user_id':recipient_user_id,
                 'from_user_id':from_user_id,
                 'from_user_name':from_user_name,
                 'from_radio_id':from_radio_id,
                 'from_radio_name':from_radio_name,
                 'read':False,
                 'params':params
                 }
        self.notifications.insert(notif)
        yamessage_signals.new_notification.send(sender=self, notification=notif)
        
    def text_for_notification(self, notification_type, params):
        from django.utils import translation
        translation.activate('fr')
        
        raw_text = unicode(yamessage_settings.NOTIF_INFOS[notification_type]['text'])
        if params is not None:
            text = raw_text % params
        else:
            text = raw_text
        return text
        
        
    def notifications_for_recipient(self, user_id, count=None, skip=0, date_greater_than=None, date_lower_than=None, read_status='all'):
        date_request = {}
        if date_greater_than is not None:
            date_request['$gt'] = date_greater_than
        if date_lower_than is not None:
            date_request['$lt'] = date_lower_than
            
        request = {}
        request['dest_user_id'] = user_id
        if len(date_request) > 0:
            request['date'] = date_request

        if read_status == 'read':
            request['read'] = True
        elif read_status == 'unread':
            request['read'] = False
        
        print request
        if count is not None:
            notifications = self.notifications.find(request).sort([('date', DESCENDING)]).skip(skip).limit(count)
        else:
            notifications = self.notifications.find(request).sort([('date', DESCENDING)]).skip(skip)
        return notifications
    
    def get_notification(self, notif_id):
        if isinstance(notif_id, str) or isinstance(notif_id, unicode):
            notif_id = ObjectId(notif_id)
        notifs = self.notifications.find({'_id': notif_id})
        if notifs.count() == 0:
            return None
        return notifs[0]
    
    def update_notification(self, notif_data):
        id_str = notif_data.get('_id', None)
        if id_str and (isinstance(id_str, str) or isinstance(id_str, unicode)):
            notif_data['_id'] = ObjectId(id_str)
        date_str = notif_data.get('date', None)
        if date_str and (isinstance(date_str, str) or isinstance(date_str, unicode)):
            if '.' in date_str:
                notif_data['date'] = datetime.datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%f")
            else:
                notif_data['date'] = datetime.datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
        
        self.notifications.update({'_id':notif_data['_id']}, notif_data)
        return self.get_notification(id_str)
        
    def delete_notification(self, notif_id):
        if isinstance(notif_id, str) or isinstance(notif_id, unicode):
            notif_id = ObjectId(notif_id)
        self.notifications.remove({'_id':notif_id})
    
    def delete_all_notifications(self, user_id):
        self.notifications.remove({'dest_user_id':user_id})
        
    