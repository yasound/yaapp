# -*- coding: utf-8 -*-
"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from models import MenusManager
from django.test import Client
from django.contrib.auth.models import User
from tastypie.models import ApiKey
import json


class TestMenus(TestCase):
    def setUp(self):
        mm = MenusManager()
        mm.clear()
        self.menu_fr = mm.default('fr')
        self.menu_en = mm.default('en')
        
    def test_add_menu(self):
        """
        Tests that a menu description can be added
        """
        mm = MenusManager()
        self.assertEqual(mm.menus_count(), 0)
        added = mm.add_menu(self.menu_fr)
        self.assertEqual(added, True)
        self.assertEqual(mm.menus_count(), 1)

    def test_add_2_menus(self):
        """
        Tests that 2 menu descriptions can be added
        """
        mm = MenusManager()
        self.assertEqual(mm.menus_count(), 0)
        added_fr = mm.add_menu(self.menu_fr)
        added_en = mm.add_menu(self.menu_en)
        self.assertEqual(added_fr, True)
        self.assertEqual(added_en, True)
        self.assertEqual(mm.menus_count(), 2)
        
    def test_get_menu(self):
        """
        Tests that awe can get a menu description
        """
        mm = MenusManager()
        self.assertEqual(mm.menus_count(), 0)
        groups = self.menu_fr['group_ids']
        language = self.menu_fr['language']
        mm.add_menu(self.menu_fr)
        x = mm.get_menu(language, groups)
        self.assertIsNotNone(x)
        
    def test_update_menu(self):
        """
        Tests that a menu description can be updated
        """
        mm = MenusManager()
        self.assertEqual(mm.menus_count(), 0)
        groups = self.menu_fr['group_ids']
        language = self.menu_fr['language']
        mm.add_menu(self.menu_fr)
        x = mm.get_menu(language, groups)
        
        new_radio_name = 'La meilleure radio'
        x['sections'][0]['name'] = new_radio_name
        
        new_favorite_url = 'api/v1/favorites'
        x['sections'][1]['entries'][1]['params']['url'] = new_favorite_url
        
        mm.update_menu(x)
        
        y = mm.get_menu(language, groups)
        self.assertEqual(y['sections'][0]['name'], new_radio_name)
        self.assertEqual(y['sections'][1]['entries'][1]['params']['url'], new_favorite_url)
        
        
        
    def test_menu_description_view(self):
        """
        Tests that the view to get the menu description works
        """
        mm = MenusManager()
        mm.add_menu(self.menu_en)
        
        user = User(email="test@yasound.com", username="test", is_superuser=False, is_staff=False)
        user.set_password('test')
        user.save()
        api_key = ApiKey.objects.get(user=user)
        c = Client()
        response = c.post('/api/v1/app_menu/')
        self.assertNotEquals(response.status_code, 200)
        response = c.get('/api/v1/app_menu/')
        self.assertNotEquals(response.status_code, 200)
        
        response = c.get('/api/v1/app_menu/', {'username':user.username, 'api_key':api_key.key})
        self.assertEqual(response.status_code, 200)
        
        menu_desc = json.loads(response.content)
        self.assertIsNotNone(menu_desc)
        
        
