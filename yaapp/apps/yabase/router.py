# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#     * Rearrange models' order
#     * Make sure each model has one field with primary_key=True
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.


########## Routers:
class YaappRouter(object):
    """A router to control all database operations on models in
    the yabase application"""
    
    def db_for_read(self, model, **hints):
        "Point all operations on yabase models to 'default'"
        if 'db_name' in dir(model._meta):
            return model._meta.db_name
        return None
    
    def db_for_write(self, model, **hints):
        "Point all operations on yabase models to 'default'"
        if 'db_name' in dir(model._meta):
            return model._meta.db_name
        return None
    
    def allow_relation(self, obj1, obj2, **hints):
        "Disallow relation between different databases"
        if 'db_name' in dir(obj1._meta) and 'db_name' in dir(obj2._meta):
            if obj1._meta.db_name != obj2._meta.db_name:
                return False
        return True
    
    def allow_syncdb(self, db, model):
        "Make sure the yabase app only appears on the 'default' db"
        if db == 'yasound':
            return False

        if model._meta.app_label == 'yaref':
            return None
        return True

class YaappRouterForTest(object):
    """A router to control all database operations on models in
    the yabase application
    
    Used when testing to allow syncdb (in memory)
    """
    
    def db_for_read(self, model, **hints):
        "Point all operations on yabase models to 'default'"
        if 'db_name' in dir(model._meta):
            return model._meta.db_name
        return None
    
    def db_for_write(self, model, **hints):
        "Point all operations on yabase models to 'default'"
        if 'db_name' in dir(model._meta):
            return model._meta.db_name
        return None
    
    def allow_relation(self, obj1, obj2, **hints):
        "Allow any relation if a model in yabase is involved"
        return True
    
    def allow_syncdb(self, db, model):
        return True
