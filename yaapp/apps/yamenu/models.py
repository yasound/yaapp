from django.db import models
from django.conf import settings
import json

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
        if not json_desc.has_key('group_ids') or not json_desc.has_key('name') or not json_desc.has_key('language'):
            return False
        
        group_ids = json_desc['group_ids']
        group_ids.sort()
        name = json_desc['name']
        language = json_desc['language']
        existing_menus = self.menus.find({'group_ids':group_ids, 'name':name, 'language':language})
        if existing_menus.count() > 0:
            if not overwrite:
                return False
            else:
                self.menus.remove({'group_ids':group_ids, 'name':name, 'language':language})
        self.menus.insert(json_desc)
        return True
    
    def get_menu(self, language, groups=[]):
        groups.sort() 
        existing_menus = self.menus.find({'group_ids':{'$in':groups}, 'language':language})
        if existing_menus.count() == 0:  
            existing_menus = self.menus.find({'group_ids':[], 'language':language})
        if existing_menus.count() == 0:
            return None
        return existing_menus[0] 

    def update_menu(self, json_desc):
        if not json_desc.has_key('group_ids') or not json_desc.has_key('name') or not json_desc.has_key('language'):
            return False
        
        group_ids = json_desc['group_ids']
        name = json_desc['name']
        language = json_desc['language']
        self.menus.update({'group_ids':group_ids, 'name':name, 'language':language}, json_desc, True, True) # upsert, multi
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
        
       


