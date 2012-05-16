# -*- coding: utf-8 -*-

from django.test import TestCase
from models import NotificationsManager
import settings as yamessage_settings
from django.contrib.auth.models import User
import datetime
import time
from django.test import Client
from tastypie.models import ApiKey
import json
from httplib import HTTP

class TestNotifications(TestCase):
    def setUp(self):
        m = NotificationsManager()
        m.notifications.drop()
        
    def test_add_notif(self):
        """
        Tests that a menu description can be added
        """
        m = NotificationsManager()
        self.assertEqual(m.notifications.count(), 0)
        
        user = User(email="test@yasound.com", username="test", is_superuser=False, is_staff=False)
        user.set_password('test')
        user.save()
        m.add_notification(user.id, yamessage_settings.TYPE_NOTIF_MESSAGE_FROM_YASOUND, {'url': 'yasound.com'})
        self.assertEqual(m.notifications.count(), 1)
        
    def test_get_notif(self):
        """
        Tests that a menu description can be added
        """
        
        d0 = datetime.datetime.now()
        time.sleep(0.2)
        
        m = NotificationsManager()
        self.assertEqual(m.notifications.count(), 0)
        
        user = User(email="test@yasound.com", username="test", is_superuser=False, is_staff=False)
        user.set_password('test')
        user.save()
        
        
        m.add_notification(user.id, yamessage_settings.TYPE_NOTIF_MESSAGE_FROM_YASOUND, {'url': 'yasound.com'})
        self.assertEqual(m.notifications.count(), 1)
        
        time.sleep(0.2)
        d1 = datetime.datetime.now()
        time.sleep(0.2)
        
        m.add_notification(user.id, yamessage_settings.TYPE_NOTIF_MESSAGE_FROM_YASOUND, {'url': 'yasound.com'})
        self.assertEqual(m.notifications.count(), 2)
        
        time.sleep(0.2)
        d2 = datetime.datetime.now()
        
        notif_cursor = m.notifications_for_recipient(user.id)
        self.assertEqual(notif_cursor.count(), 2)
        
        notif_cursor = m.notifications_for_recipient(user.id, date_greater_than=d0, date_lower_than=d2)
        self.assertEqual(notif_cursor.count(), 2)
        
        notif_cursor = m.notifications_for_recipient(user.id, date_greater_than=d0)
        self.assertEqual(notif_cursor.count(), 2)
        
        notif_cursor = m.notifications_for_recipient(user.id, date_lower_than=d2)
        self.assertEqual(notif_cursor.count(), 2)
        
        notif_cursor = m.notifications_for_recipient(user.id, date_greater_than=d0, date_lower_than=d1)
        self.assertEqual(notif_cursor.count(), 1)
        
        notif_cursor = m.notifications_for_recipient(user.id, date_greater_than=d1, date_lower_than=d2)
        self.assertEqual(notif_cursor.count(), 1)
        
        notif_cursor = m.notifications_for_recipient(user.id, date_lower_than=d1)
        self.assertEqual(notif_cursor.count(), 1)
        
        notif_cursor = m.notifications_for_recipient(user.id, date_greater_than=d1)
        self.assertEqual(notif_cursor.count(), 1)
        
        notif_cursor = m.notifications_for_recipient(user.id, date_lower_than=d0)
        self.assertEqual(notif_cursor.count(), 0)
        
        notif_cursor = m.notifications_for_recipient(user.id, date_greater_than=d2)
        self.assertEqual(notif_cursor.count(), 0)
        
        # count
        notif_cursor = m.notifications_for_recipient(user.id, count=1)
        self.assertEqual(notif_cursor.count(True), 1)
        
        # skip
        notif_cursor = m.notifications_for_recipient(user.id, skip=1)
        self.assertEqual(notif_cursor.count(True), 1)
        
    def test_update_notification(self):
        user = User(email="test@yasound.com", username="test", is_superuser=False, is_staff=False)
        user.set_password('test')
        user.save()
        
        m = NotificationsManager()
        m.add_notification(user.id, yamessage_settings.TYPE_NOTIF_MESSAGE_FROM_YASOUND, {'url': 'yasound.com'})
        m.add_notification(user.id, yamessage_settings.TYPE_NOTIF_MESSAGE_FROM_YASOUND, {'url': 'yasound.com'})
        m.add_notification(user.id, yamessage_settings.TYPE_NOTIF_MESSAGE_FROM_YASOUND, {'url': 'yasound.com'})
        
        notifs = m.notifications_for_recipient(user.id)
        n = notifs[0]
        notif_id = n['_id']
        
        n['read'] = True
        n_modified = m.update_notification(n)
        self.assertIsNotNone(n_modified)
        
        n2 = m.get_notification(notif_id)
        self.assertIsNotNone(n2)
        self.assertEqual(n2['read'], True)
        
        # test get notif with id as a string
        n3 = m.get_notification(str(notif_id))
        self.assertIsNotNone(n3)
        self.assertEqual(n3['read'], True)
        
    def test_delete_notification(self):
        user = User(email="test@yasound.com", username="test", is_superuser=False, is_staff=False)
        user.set_password('test')
        user.save()
        
        m = NotificationsManager()
        m.add_notification(user.id, yamessage_settings.TYPE_NOTIF_MESSAGE_FROM_YASOUND, {'url': 'yasound.com'})
        m.add_notification(user.id, yamessage_settings.TYPE_NOTIF_MESSAGE_FROM_YASOUND, {'url': 'yasound.com'})
        m.add_notification(user.id, yamessage_settings.TYPE_NOTIF_MESSAGE_FROM_YASOUND, {'url': 'yasound.com'})
        
        notifs = m.notifications_for_recipient(user.id)
        original_count = notifs.count()
        n = notifs[0]
        notif_id = n['_id']
        
        m.delete_notification(notif_id)
        notifs = m.notifications_for_recipient(user.id)
        self.assertEqual(notifs.count(), original_count - 1)
        original_count = notifs.count()
        
        n = notifs[0]
        notif_id = n['_id']
        m.delete_notification(str(notif_id)) # try with id as a string
        notifs = m.notifications_for_recipient(user.id)
        self.assertEqual(notifs.count(), original_count - 1)
        
        
    def test_get_notifications_view(self):
        user = User(email="test@yasound.com", username="test", is_superuser=False, is_staff=False)
        user.set_password('test')
        user.save()
        
        m = NotificationsManager()
        m.add_notification(user.id, yamessage_settings.TYPE_NOTIF_MESSAGE_FROM_YASOUND, {'url': 'yasound.com'})
        m.add_notification(user.id, yamessage_settings.TYPE_NOTIF_MESSAGE_FROM_YASOUND, {'url': 'yasound.com'})
        m.add_notification(user.id, yamessage_settings.TYPE_NOTIF_MESSAGE_FROM_YASOUND, {'url': 'yasound.com'})
        
        api_key = ApiKey.objects.get(user=user)
        c = Client()
        
        response = c.get('/api/v1/notifications/', {'username':user.username, 'api_key':api_key.key})
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(data)
        self.assertEqual(len(data), 3)
        
    def test_get_notification_view(self):
        user = User(email="test@yasound.com", username="test", is_superuser=False, is_staff=False)
        user.set_password('test')
        user.save()
        
        m = NotificationsManager()
        m.add_notification(user.id, yamessage_settings.TYPE_NOTIF_MESSAGE_FROM_YASOUND, {'url': 'yasound.com'})
        m.add_notification(user.id, yamessage_settings.TYPE_NOTIF_MESSAGE_FROM_YASOUND, {'url': 'yasound.com'})
        m.add_notification(user.id, yamessage_settings.TYPE_NOTIF_MESSAGE_FROM_YASOUND, {'url': 'yasound.com'})
        
        notifs = m.notifications_for_recipient(user.id)
        self.assertEqual(notifs.count(), 3)
        n = notifs[0]
        notif_id = str(n['_id'])
        
        api_key = ApiKey.objects.get(user=user)
        c = Client()
        
        response = c.get('/api/v1/notification/%s/' % notif_id, {'username':user.username, 'api_key':api_key.key})
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertIsNotNone(data)
        self.assertEqual(data['_id'], notif_id)
        
        
    def test_update_notification_view(self):
        user = User(email="test@yasound.com", username="test", is_superuser=False, is_staff=False)
        user.set_password('test')
        user.save()
        
        m = NotificationsManager()
        m.add_notification(user.id, yamessage_settings.TYPE_NOTIF_MESSAGE_FROM_YASOUND, {'url': 'yasound.com'})
        m.add_notification(user.id, yamessage_settings.TYPE_NOTIF_MESSAGE_FROM_YASOUND, {'url': 'yasound.com'})
        m.add_notification(user.id, yamessage_settings.TYPE_NOTIF_MESSAGE_FROM_YASOUND, {'url': 'yasound.com'})
        
        notifs = m.notifications_for_recipient(user.id)
        self.assertEqual(notifs.count(), 3)
        n = notifs[0]
        notif_id = str(n['_id'])
        
        api_key = ApiKey.objects.get(user=user)
        c = Client()
        
        response = c.get('/api/v1/notification/%s/' % notif_id, {'username':user.username, 'api_key':api_key.key})
        self.assertEqual(response.status_code, 200)
        
        n = json.loads(response.content)
        n['read'] = True
        
        response = c.put('/api/v1/update_notification/%s/?username=%s&api_key=%s' % (notif_id, user.username, api_key.key), n)
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertIsNotNone(data)
        self.assertEqual(data['_id'], notif_id)
        
        
    def test_delete_notification_view(self):
        user = User(email="test@yasound.com", username="test", is_superuser=False, is_staff=False)
        user.set_password('test')
        user.save()
        
        m = NotificationsManager()
        m.add_notification(user.id, yamessage_settings.TYPE_NOTIF_MESSAGE_FROM_YASOUND, {'url': 'yasound.com'})
        m.add_notification(user.id, yamessage_settings.TYPE_NOTIF_MESSAGE_FROM_YASOUND, {'url': 'yasound.com'})
        m.add_notification(user.id, yamessage_settings.TYPE_NOTIF_MESSAGE_FROM_YASOUND, {'url': 'yasound.com'})
        
        notifs = m.notifications_for_recipient(user.id)
        self.assertEqual(notifs.count(), 3)
        n = notifs[0]
        notif_id = str(n['_id'])
        
        api_key = ApiKey.objects.get(user=user)
        c = Client()
        
        response = c.delete('/api/v1/delete_notification/%s/?username=%s&api_key=%s' % (notif_id, user.username, api_key.key))
        self.assertEqual(response.status_code, 200)
        
        notifs = m.notifications_for_recipient(user.id)
        self.assertEqual(notifs.count(), 2)
