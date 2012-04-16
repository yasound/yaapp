from django.db.models import F
from django.db import transaction

@transaction.commit_manually
def flush_transaction():
    """
    Flush the current transaction so we don't read stale data

    Use in long running processes to make sure fresh data is read from
    the database.  This is a problem with MySQL and the default
    transaction mode.  You can fix it by setting
    "transaction-isolation = READ-COMMITTED" in my.cnf or by calling
    this function at the appropriate moment
    
    
    see http://stackoverflow.com/questions/3346124/how-do-i-force-django-to-ignore-any-caches-and-reload-data
    
    """
    transaction.commit()

def atomic_inc(instance, field, value):
    """
    atomic increment field value
    
    example :

    radio = Radio.objects.get(id=75)
    yabase_utils.atomic_inc(radio, 'anonymous_audience', 1)
    
    """
    new_value = F(field)+value
    kwargs = {field:new_value}
    instance.__class__.objects.filter(id=instance.id).update(**kwargs)