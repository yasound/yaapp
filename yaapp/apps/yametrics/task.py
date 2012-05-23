from account.models import Device
from celery.task import task
from yabase.models import Radio
import datetime
from yametrics.models import TimedMetricsManager

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

@task(ignore_result=True)
def calculate_top_missing_songs_task():
    from models import TopMissingSongsManager
    tm = TopMissingSongsManager()
    tm.calculate()
        
@task(ignore_result=True)
def daily_metrics():
    from models import GlobalMetricsManager
    mm = GlobalMetricsManager()

    device_count = Device.objects.filter(ios_token__gte=0).count()
    mm.set_daily_value('device_count', device_count)
    
    ready_radio_count = Radio.objects.filter(ready=True).count()
    mm.set_daily_value('ready_radio_count', ready_radio_count)
    
@task(ignore_result=True)
def async_animator_activity(user_id):
    from models import UserMetricsManager
    
    um = UserMetricsManager()
    doc = um.get_doc(user_id)
    
    last_animator_activity_date = doc['last_animator_activity_date'] if 'last_animator_activity_date' in doc else None
    last_animator_slot = doc['last_animator_activity_slot'] if 'last_animator_activity_slot' in doc else None
    
    now = datetime.datetime.now()
    days = 0
    if last_animator_activity_date:
        diff = (now - last_animator_activity_date)
        days = diff.days
        last_action = diff.total_seconds()
        if last_action < 60*60:
            # we skip the same action from user within one hour
            return 

    tm = TimedMetricsManager()
    if last_animator_slot:
        tm.inc_value(last_animator_slot, 'animator_activity', -1)
    
    if days >= 0:
        slot = '24h'
    elif days in range(1, 3):
        slot = '3d'
    elif days in range(4, 7):
        slot = '7d'
    elif days in range(8, 15):
        slot = '15d'
    else:
        slot = '90d'
    
    tm.inc_value(slot, 'animator_activity', 1)
    
    um.set_value(user_id, 'last_animator_activity_slot', slot)
    um.set_value(user_id, 'last_animator_activity_date', now)
    um.inc_value(user_id, 'animator_activity', 1)
        