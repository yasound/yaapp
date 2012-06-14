from django.db import models
from django.conf import settings
import json
from distutils.version import StrictVersion
from Image import NONE
import yabase.settings as yabase_settings
from account.models import get_techtour_group
from yabase.models import Radio

##############################
### list of menu entry type
##############################
# radio
# radio_list
# user
# user_list
# web_page
# radio_search
# my_radio
# friends
# notifications
# stats
# settings
# programming
# logout

class MenusManager():
    """
    Helper class to store and retrieve application menu descriptions
    """
    def __init__(self):
        self.menus = settings.MONGO_DB.menus  
        
    def clear(self):
        self.menus.drop()
        
    def menus_count(self):
        return self.menus.count()      
    
    def add_menu_string(self, json_desc_string, overwrite=False):
        json_desc = json.loads(json_desc_string)
        return self.add_menu(json_desc, overwrite)
    
    def add_menu(self, json_desc, overwrite=False):
        if not json_desc.has_key('name') or not json_desc.has_key('language'):
            return False
        
        self.menus.insert(json_desc)
        return True
    
    def _get_menu_internal(self, language, groups, app_id, app_version):
        groups.sort() 
        if groups:
            if len(groups) > 0:
                if app_id:
                    menus = self.menus.find({'language':language, 'group_ids':{'$in':groups}, 'app.app_id':app_id})
                else:
                    menus = self.menus.find({'language':language, 'group_ids':{'$in':groups}})
            else:
                if app_id:
                    menus = self.menus.find({'language':language, 'group_ids':groups, 'app.app_id':app_id})
                else:
                    menus = self.menus.find({'language':language, 'group_ids':groups})
        elif app_id:
            menus = self.menus.find({'language':language, 'app.app_id':app_id})
        else:
            menus = self.menus.find({'language':language})
        
        version = StrictVersion(app_version) if app_version else None
        final_menus = []
        for m in menus:
            if version: # if a version is specified, the menu must follow this constraint
                if not m.has_key('app'):
                    continue
                if not m['app'].has_key('app_version'):
                    continue
                if m['app']['app_version'].has_key('min') and version < StrictVersion(m['app']['app_version']['min']):
                    continue
                if m['app']['app_version'].has_key('max') and version > StrictVersion(m['app']['app_version']['max']):
                    continue
            else:
                if m.has_key('app') and m['app'].has_key('app_version'):
                    continue # must not choose this menu because it has version restrictions and no version is given
            final_menus.append(m)
                    
        if len(final_menus) == 0:
            return None
        return final_menus[0]
    
    def get_menu(self, language, groups=[], app_id=None, app_version=None, strict_search=False):
        m = self._get_menu_internal(language, groups, app_id, app_version)
        if strict_search:
            return m
        
        if m == None:
            m = self._get_menu_internal(language, [], app_id, app_version)
        if m == None:
            m = self._get_menu_internal(language, [], app_id, None)
        if m == None:
            m = self._get_menu_internal(language, [], None, None)
        return m
        
            
    def update_menu(self, json_desc):
        if not json_desc.has_key('_id'):
            return False
        
        obj_id = json_desc['_id']
        self.menus.update({'_id':obj_id}, json_desc, True, True) # upsert, multi
        return True
    
    def defaults(self):
        fr = {'sections': [{'name': 'Ma radio', 'entries': [{'image': 'IconMyRadio', 'type': 'my_radio', 'id': 'myRadio', 'name': 'Ma radio'}]}, {'name': 'Radios', 'entries': [{'image': 'IconRadiosFriends', 'type': 'friends', 'id': 'radioMyFriends', 'name': 'Mes amis'}, {'params': {'url': '/api/v1/favorite_radio', 'genre_selection': False}, 'image': 'IconRadiosFavorites', 'type': 'radio_list', 'id': 'radioMyFavorites', 'name': 'Mes favoris'}, {'params': {'url': '/api/v1/selected_radio'}, 'image': 'IconRadiosSelection', 'type': 'radio_list', 'id': 'radioSelection', 'name': 'S\xc3\xa9lection'}, {'params': {'url': '/api/v1/top_radio'}, 'image': 'IconLeaderboard', 'type': 'radio_list', 'id': 'radioTop', 'name': 'Top'}, {'image': 'IconRadiosSearch', 'type': 'search_radio', 'id': 'radioSearch', 'name': 'Recherche'}]}, {'name': 'Moi', 'entries': [{'image': 'IconMeNotifs', 'type': 'notifications', 'id': 'meNotifications', 'name': 'Mes notifications'}, {'image': 'IconMeStats', 'type': 'stats', 'id': 'meStats', 'name': 'Mes statistiques'}, {'image': 'IconMePlaylists', 'type': 'programming', 'id': 'meProgramming', 'name': 'Ma programmation'}, {'image': 'IconMeSettings', 'type': 'settings', 'id': 'meSettings', 'name': 'Param\xc3\xa8tres'}]}, {'name': 'Divers', 'entries': [{'params': {'url': 'legal/eula.html'}, 'image': 'IconMiscLegal', 'type': 'web_page', 'id': 'miscLegal', 'name': "Conditions d'utilisation"}, {'image': 'IconMiscLogout', 'type': 'logout', 'id': 'miscLogout', 'name': 'Se d\xc3\xa9connecter'}]}], 'name': 'default', 'language': 'fr', 'group_ids':[]}
        en = {'sections': [{'name': 'My radio', 'entries': [{'image': 'IconMyRadio', 'type': 'my_radio', 'id': 'myRadio', 'name': 'My radio'}]}, {'name': 'Radios', 'entries': [{'image': 'IconRadiosFriends', 'type': 'friends', 'id': 'radioMyFriends', 'name': 'My friends'}, {'params': {'url': '/api/v1/favorite_radio', 'genre_selection': False}, 'image': 'IconRadiosFavorites', 'type': 'radio_list', 'id': 'radioMyFavorites', 'name': 'My favorites'}, {'params': {'url': '/api/v1/selected_radio'}, 'image': 'IconRadiosSelection', 'type': 'radio_list', 'id': 'radioSelection', 'name': 'Selection'}, {'params': {'url': '/api/v1/top_radio'}, 'image': 'IconLeaderboard', 'type': 'radio_list', 'id': 'radioTop', 'name': 'Top'}, {'image': 'IconRadiosSearch', 'type': 'search_radio', 'id': 'radioSearch', 'name': 'Search'}]}, {'name': 'Me', 'entries': [{'image': 'IconMeNotifs', 'type': 'notifications', 'id': 'meNotifications', 'name': 'My notifications'}, {'image': 'IconMeStats', 'type': 'stats', 'id': 'meStats', 'name': 'My stats'}, {'image': 'IconMePlaylists', 'type': 'programming', 'id': 'meProgramming', 'name': 'Programming'}, {'image': 'IconMeSettings', 'type': 'settings', 'id': 'meSettings', 'name': 'Settings'}]}, {'name': 'Miscellaneous', 'entries': [{'params': {'url': 'legal/eula.html'}, 'image': 'IconMiscLegal', 'type': 'web_page', 'id': 'miscLegal', 'name': 'Terms of Use'}, {'image': 'IconMiscLogout', 'type': 'logout', 'id': 'miscLogout', 'name': 'Log out'}]}], 'name': 'default', 'language': 'en', 'group_ids':[]}
        defaults = [fr, en]
        return defaults
    
    def default(self, language):
        for i in self.defaults():
            if i.has_key('language') and i['language'] == language:
                return i
        return None
    
    def install_defaults(self):
        for i in self.defaults():
            self.add_menu(i, overwrite=True)
            
    def install_techtour(self):
        techtour_section_fr = {'name': 'Tech Tour', 'entries': []}
        techtour_section_en = {'name': 'Tech Tour', 'entries': []}
        
        # add entry for 'Techtour lounge' radio
        try:
            techtour_radio = Radio.objects.get(name__iexact='Techtour Lounge')
            techtour_radio_id = techtour_radio.id
            
            radio_entry_fr = {'image': 'IconMyRadio', 'type': 'radio', 'id': 'myRadio', 'name': 'Techtour lounge', 'params':{'radio_id':techtour_radio_id}}
            techtour_section_fr['entries'].append(radio_entry_fr)
            
            radio_entry_en = {'image': 'IconMyRadio', 'type': 'radio', 'id': 'myRadio', 'name': 'Techtour lounge', 'params':{'radio_id':techtour_radio_id}}
            techtour_section_en['entries'].append(radio_entry_en)
        except Radio.DoesNotExist:
            pass
        
        # add entry for techtour radio list
        techtour_group = get_techtour_group()
        techtour_group_ids = [techtour_group.id] 
        
        radios_techtour_fr = {'image': 'IconRadiosFavorites', 'type': 'radio_list', 'id': 'radiosTechtour', 'name': 'Radios Techtour', 'params':{'url':'api/v1/techtour_radio', 'genre_selection': False}}
        techtour_section_fr['entries'].append(radios_techtour_fr)
        
        radios_techtour_en = {'image': 'IconRadiosFavorites', 'type': 'radio_list', 'id': 'radiosTechtour', 'name': 'Techtour radios', 'params':{'url':'api/v1/techtour_radio', 'genre_selection': False}}
        techtour_section_en['entries'].append(radios_techtour_en)
                
        # menus with techtour section
        techtour_fr = {'sections': [{'name': 'Ma radio', 'entries': [{'image': 'IconMyRadio', 'type': 'my_radio', 'id': 'myRadio', 'name': 'Ma radio'}]}, techtour_section_fr, {'name': 'Radios', 'entries': [{'image': 'IconRadiosFriends', 'type': 'friends', 'id': 'radioMyFriends', 'name': 'Mes amis'}, {'params': {'url': '/api/v1/favorite_radio', 'genre_selection': False}, 'image': 'IconRadiosFavorites', 'type': 'radio_list', 'id': 'radioMyFavorites', 'name': 'Mes favoris'}, {'params': {'url': '/api/v1/selected_radio'}, 'image': 'IconRadiosSelection', 'type': 'radio_list', 'id': 'radioSelection', 'name': 'S\xc3\xa9lection'}, {'params': {'url': '/api/v1/top_radio'}, 'image': 'IconLeaderboard', 'type': 'radio_list', 'id': 'radioTop', 'name': 'Top'}, {'image': 'IconRadiosSearch', 'type': 'search_radio', 'id': 'radioSearch', 'name': 'Recherche'}]}, {'name': 'Moi', 'entries': [{'image': 'IconMeNotifs', 'type': 'notifications', 'id': 'meNotifications', 'name': 'Mes notifications'}, {'image': 'IconMeStats', 'type': 'stats', 'id': 'meStats', 'name': 'Mes statistiques'}, {'image': 'IconMePlaylists', 'type': 'programming', 'id': 'meProgramming', 'name': 'Ma programmation'}, {'image': 'IconMeSettings', 'type': 'settings', 'id': 'meSettings', 'name': 'Param\xc3\xa8tres'}]}, {'name': 'Divers', 'entries': [{'params': {'url': 'legal/eula.html'}, 'image': 'IconMiscLegal', 'type': 'web_page', 'id': 'miscLegal', 'name': "Conditions d'utilisation"}, {'image': 'IconMiscLogout', 'type': 'logout', 'id': 'miscLogout', 'name': 'Se d\xc3\xa9connecter'}]}], 'name': 'default', 'language': 'fr', 'group_ids':techtour_group_ids, 'app':{'app_id':yabase_settings.IPHONE_TECH_TOUR_APPLICATION_IDENTIFIER}}
        techtour_en = {'sections': [{'name': 'My radio', 'entries': [{'image': 'IconMyRadio', 'type': 'my_radio', 'id': 'myRadio', 'name': 'My radio'}]}, techtour_section_en, {'name': 'Radios', 'entries': [{'image': 'IconRadiosFriends', 'type': 'friends', 'id': 'radioMyFriends', 'name': 'My friends'}, {'params': {'url': '/api/v1/favorite_radio', 'genre_selection': False}, 'image': 'IconRadiosFavorites', 'type': 'radio_list', 'id': 'radioMyFavorites', 'name': 'My favorites'}, {'params': {'url': '/api/v1/selected_radio'}, 'image': 'IconRadiosSelection', 'type': 'radio_list', 'id': 'radioSelection', 'name': 'Selection'}, {'params': {'url': '/api/v1/top_radio'}, 'image': 'IconLeaderboard', 'type': 'radio_list', 'id': 'radioTop', 'name': 'Top'}, {'image': 'IconRadiosSearch', 'type': 'search_radio', 'id': 'radioSearch', 'name': 'Search'}]}, {'name': 'Me', 'entries': [{'image': 'IconMeNotifs', 'type': 'notifications', 'id': 'meNotifications', 'name': 'My notifications'}, {'image': 'IconMeStats', 'type': 'stats', 'id': 'meStats', 'name': 'My stats'}, {'image': 'IconMePlaylists', 'type': 'programming', 'id': 'meProgramming', 'name': 'Programming'}, {'image': 'IconMeSettings', 'type': 'settings', 'id': 'meSettings', 'name': 'Settings'}]}, {'name': 'Miscellaneous', 'entries': [{'params': {'url': 'legal/eula.html'}, 'image': 'IconMiscLegal', 'type': 'web_page', 'id': 'miscLegal', 'name': 'Terms of Use'}, {'image': 'IconMiscLogout', 'type': 'logout', 'id': 'miscLogout', 'name': 'Log out'}]}], 'name': 'default', 'language': 'en', 'group_ids':techtour_group_ids, 'app':{'app_id':yabase_settings.IPHONE_TECH_TOUR_APPLICATION_IDENTIFIER}}
        self.add_menu(techtour_fr, overwrite=True)
        self.add_menu(techtour_en, overwrite=True)
        
    
    def install_v2(self):
        fr = {
              'name': 'v2',
              'language': 'fr',
              'group_ids': [],
              'app': {
                      'app_id': yabase_settings.IPHONE_DEFAULT_APPLICATION_IDENTIFIER,
                      'app_version': {'min': '2.0'}
                      },
              'sections': [
                            {'name': 'Session', 'entries': 
                                [
                                {'image': 'IconMiscLogout', 'type': 'logout', 'id': 'miscLogout', 'name': 'Se connecter'},
                                {'image': 'IconMyRadio', 'type': 'my_radio', 'id': 'myRadio', 'name': 'Ma radio'}
                                ]}, 
                            {'name': 'Radios', 'entries': 
                                [
                                {'image': 'IconRadiosFriends', 'type': 'friends', 'id': 'radioMyFriends', 'name': 'Mes amis'}, 
                                {'params': {'url': '/api/v1/favorite_radio', 'genre_selection': False}, 'image': 'IconRadiosFavorites', 'type': 'radio_list', 'id': 'radioMyFavorites', 'name': 'Mes favoris'}, 
                                {'params': {'url': '/api/v1/selected_radio'}, 'image': 'IconRadiosSelection', 'type': 'radio_list', 'id': 'radioSelection', 'name': 'S\xc3\xa9lection'}, 
                                {'params': {'url': '/api/v1/top_radio'}, 'image': 'IconLeaderboard', 'type': 'radio_list', 'id': 'radioTop', 'name': 'Top'}, 
                                {'image': 'IconRadiosSearch', 'type': 'search_radio', 'id': 'radioSearch', 'name': 'Recherche'}
                                ]}, 
                            {'name': 'Moi', 'entries': 
                                [
                                {'image': 'IconMeNotifs', 'type': 'notifications', 'id': 'meNotifications', 'name': 'Mes notifications'}, 
                                {'image': 'IconMeStats', 'type': 'stats', 'id': 'meStats', 'name': 'Mes statistiques'}, 
                                {'image': 'IconMePlaylists', 'type': 'programming', 'id': 'meProgramming', 'name': 'Ma programmation'}, 
                                {'image': 'IconMeSettings', 'type': 'settings', 'id': 'meSettings', 'name': 'Param\xc3\xa8tres'}
                                ]}, 
                            {'name': 'Divers', 'entries': 
                                [
                                {'params': {'url': 'legal/eula.html'}, 'image': 'IconMiscLegal', 'type': 'web_page', 'id': 'miscLegal', 'name': "Conditions d'utilisation"}
                                ]}
                            ]
              }
        
        en = {
              'name': 'v2',
              'language': 'en',
              'group_ids': [],
              'app': {
                      'app_id': yabase_settings.IPHONE_DEFAULT_APPLICATION_IDENTIFIER,
                      'app_version': {'min': '2.0'}
                      },
              'sections': [
                            {'name': 'Session', 'entries': 
                                [
                                {'image': 'IconMiscLogout', 'type': 'logout', 'id': 'miscLogout', 'name': 'Log in'},
                                {'image': 'IconMyRadio', 'type': 'my_radio', 'id': 'myRadio', 'name': 'My radio'}
                                ]}, 
                            {'name': 'Radios', 'entries': 
                                [
                                {'image': 'IconRadiosFriends', 'type': 'friends', 'id': 'radioMyFriends', 'name': 'My friends'}, 
                                {'params': {'url': '/api/v1/favorite_radio', 'genre_selection': False}, 'image': 'IconRadiosFavorites', 'type': 'radio_list', 'id': 'radioMyFavorites', 'name': 'My favorites'}, 
                                {'params': {'url': '/api/v1/selected_radio'}, 'image': 'IconRadiosSelection', 'type': 'radio_list', 'id': 'radioSelection', 'name': 'Selection'}, 
                                {'params': {'url': '/api/v1/top_radio'}, 'image': 'IconLeaderboard', 'type': 'radio_list', 'id': 'radioTop', 'name': 'Top'}, 
                                {'image': 'IconRadiosSearch', 'type': 'search_radio', 'id': 'radioSearch', 'name': 'Search'}
                                ]}, 
                            {'name': 'Me', 'entries': 
                                [
                                {'image': 'IconMeNotifs', 'type': 'notifications', 'id': 'meNotifications', 'name': 'My notifications'}, 
                                {'image': 'IconMeStats', 'type': 'stats', 'id': 'meStats', 'name': 'My stats'}, 
                                {'image': 'IconMePlaylists', 'type': 'programming', 'id': 'meProgramming', 'name': 'Programming'}, 
                                {'image': 'IconMeSettings', 'type': 'settings', 'id': 'meSettings', 'name': 'Settings'}
                                ]}, 
                            {'name': 'Miscellaneous', 'entries': 
                                [
                                {'params': {'url': 'legal/eula.html'}, 'image': 'IconMiscLegal', 'type': 'web_page', 'id': 'miscLegal', 'name': 'Terms of Use'}
                                ]}
                            ]
              }
        
        self.add_menu(fr, overwrite=True)
        self.add_menu(en, overwrite=True)
            
            
    
        
       


