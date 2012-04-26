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
        if not json_desc.has_key('name') or not json_desc.has_key('language'):
            return False
        
        name = json_desc['name']
        language = json_desc['language']
        existing_menus = self.menus.find({'name':name, 'language':language})
        if existing_menus.count() > 0:
            if not overwrite:
                return False
            else:
                self.menus.remove({'name':name, 'language':language})
        self.menus.insert(json_desc)
        return True
    
    def get_menu(self, name, language):
        existing_menus = self.menus.find({'name':name, 'language':language})
        if existing_menus.count() == 0:  
            return None
        return existing_menus[0]  
    
    def remove_menu(self, name, language):
        self.menus.remove({'name':name, 'language':language})

    def update_menu(self, json_desc):
        if not json_desc.has_key('name') or not json_desc.has_key('language'):
            return False
        
        name = json_desc['name']
        language = json_desc['language']
        self.menus.update({'name':name, 'language':language}, json_desc, True, True) # upsert, multi
        return True
        
       

