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
	if model._meta.app_label != 'yabase':
            return None
        if model._meta.db_table[:8] == 'yasound_':
            return 'yasound'
        return 'default'

    def db_for_write(self, model, **hints):
        "Point all operations on yabase models to 'default'"
	if model._meta.app_label != 'yabase':
            return None
        if model._meta.db_table[:8] == 'yasound_':
            return 'yasound'
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        "Allow any relation if a model in yabase is involved"
	if model._meta.app_label != 'yabase':
            return None
        if model._meta.db_table[:8] != 'yasound_':
            return True
        return False

    def allow_syncdb(self, db, model):
        "Make sure the yabase app only appears on the 'default' db"
	if model._meta.app_label != 'yabase':
            return None
        if db == 'yasound':
            return False
        return True

