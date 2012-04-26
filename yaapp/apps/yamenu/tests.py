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
        self.menu_fr = {'sections': [{'name': 'Ma radio', 'entries': [{'image': '', 'type': 'my_radio', 'name': 'Ma Radio'}]}, {'name': 'Radios', 'entries': [{'image': '', 'type': 'friends', 'name': 'Mes amis'}, {'params': {'url': '/api/v1/favorite_radio'}, 'image': '', 'type': 'radio_list', 'name': 'Mes favoris'}, {'params': {'url': '/api/v1/selected_radio'}, 'image': '', 'type': 'radio_list', 'name': 'Sélection'}, {'params': {'url': '/api/v1/top_radio'}, 'image': '', 'type': 'radio_list', 'name': 'Top'}, {'image': '', 'type': 'search_radio', 'name': 'Recherche'}]}, {'name': 'Moi', 'entries': [{'image': '', 'type': 'notifications', 'name': 'Mes notifications'}, {'image': '', 'type': 'stats', 'name': 'Mes statistiques'}, {'image': '', 'type': 'programming', 'name': 'Ma programmation'}, {'image': '', 'type': 'settings', 'name': 'Paramètres'}]}, {'name': 'Divers', 'entries': [{'params': {'url': 'legal/eula.html'}, 'image': '', 'type': 'web_page', 'name': u"Conditions d'utilisation"}, {'image': '', 'type': 'logout', 'name': 'Se déconnecter'}]}], 'name': 'default', 'language': 'fr'}
        self.menu_en = {'sections': [{'name': 'My radio', 'entries': [{'image': '', 'type': 'my_radio', 'name': 'My Radio'}]}, {'name': 'Radios', 'entries': [{'image': '', 'type': 'friends', 'name': 'My friends'}, {'type': 'radio_list', 'image': '', 'params': {'url': '/api/v1/favorite_radio'}, 'name': 'My favorites'}, {'type': 'radio_list', 'image': '', 'params': {'url': '/api/v1/selected_radio'}, 'name': 'Selection'}, {'type': 'radio_list', 'image': '', 'params': {'url': '/api/v1/top_radio'}, 'name': 'Top'}, {'image': '', 'type': 'search_radio', 'name': 'Search'}]}, {'name': 'Me', 'entries': [{'image': '', 'type': 'notifications', 'name': 'My notifications'}, {'image': '', 'type': 'stats', 'name': 'My stats'}, {'image': '', 'type': 'programming', 'name': 'Programming'}, {'image': '', 'type': 'settings', 'name': 'Settings'}]}, {'name': 'Miscellaneous', 'entries': [{'type': 'web_page', 'image': '', 'params': {'url': 'legal/eula.html'}, 'name': 'Terms of Use'}, {'image': '', 'type': 'logout', 'name': 'Log out'}]}], 'name': 'default', 'language': 'en'}
        
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
        name = self.menu_fr['name']
        language = self.menu_fr['language']
        mm.add_menu(self.menu_fr)
        x = mm.get_menu(name, language)
        self.assertIsNotNone(x)
        
    def test_update_menu(self):
        """
        Tests that a menu description can be updated
        """
        mm = MenusManager()
        self.assertEqual(mm.menus_count(), 0)
        name = self.menu_fr['name']
        language = self.menu_fr['language']
        mm.add_menu(self.menu_fr)
        x = mm.get_menu(name, language)
        
        new_radio_name = 'La meilleure radio'
        x['sections'][0]['name'] = new_radio_name
        
        new_favorite_url = 'api/v1/favorites'
        x['sections'][1]['entries'][1]['params']['url'] = new_favorite_url
        
        mm.update_menu(x)
        
        y = mm.get_menu(name, language)
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
        
        
