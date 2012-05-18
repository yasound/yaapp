from account.models import Device
from celery.task import task

@task(ignore_result=True)
def async_inc_global_value(key, value):  
    from models import GlobalMetricsManager
    mm = GlobalMetricsManager()
    mm.inc_global_value(key, value)

@task(ignore_result=True)
def async_inc_radio_value(radio_id, key, value):  
    from models import RadioMetricsManager
    rm = RadioMetricsManager()
    rm.inc_value(radio_id, key, value)

@task
def calculate_top_missing_songs_task():
    from models import TopMissingSongsManager
    tm = TopMissingSongsManager()
    tm.calculate()
        
@task
def daily_metrics():
    from models import GlobalMetricsManager
    mm = GlobalMetricsManager()

    device_count = Device.objects.filter(ios_token__gte=0).count()
    mm.set_daily_value('device_count', device_count)