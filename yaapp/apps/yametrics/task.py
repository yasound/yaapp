from celery.task import task

@task(ignore_result=True)
def async_inc_global_value(key, value):  
    from models import MetricsManager
    mm = MetricsManager()
    mm.inc_global_value(key, value)
