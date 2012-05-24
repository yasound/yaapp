from account.models import Device
from celery.task import task
from yabase.models import Radio
import datetime
from yahistory.models import UserHistory

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
    
    update_activities(['listen_activity',
                       'animator_activity', 
                       'share_facebook_activity',
                       'share_twitter_activity',
                       'share_email_activity',
                       ])
    
@task(ignore_result=True)
def async_activity(user_id, activity):
    """
    Process activity (animator for instance) :
    
    * update user document with the following fields:
      * last_activity_date
      * last_activity_slot
      * activity
    * update timed documents with the following fields:
      * activity
    """
    from models import UserMetricsManager, TimedMetricsManager
    
    um = UserMetricsManager()
    doc = um.get_doc(user_id)
    
    key_last_date = 'last_%s_date' % (activity) 
    key_last_slot = 'last_%s_slot' % (activity) 
    
    last_animator_activity_date, last_animator_activity_slot = None, None
    if doc:
        last_animator_activity_date = doc[key_last_date] if key_last_date in doc else None
        last_animator_activity_slot = doc[key_last_slot] if key_last_slot in doc else None
    
    now = datetime.datetime.now()
    days = 0
    if last_animator_activity_date:
        diff = (now - last_animator_activity_date)
        days = diff.days
        last_action = diff.total_seconds()
        if last_action < 60*60:
            # we skip the same action from user within one hour
            return 

    # update timed document
    tm = TimedMetricsManager()
    if last_animator_activity_slot:
        # remove from previous slot
        tm.inc_value(last_animator_activity_slot, activity, -1)
    
    # add to current slot
    slot = tm.slot(days)
    tm.inc_value(slot, activity, 1)
    
    # update currrent user document
    um.set_value(user_id, key_last_slot, slot)
    um.set_value(user_id, key_last_date, now)
    um.inc_value(user_id, activity, 1)

def update_activities(activities):
    """
    Periodically move timed metrics from one slot to another
    """
    from models import UserMetricsManager, TimedMetricsManager
    
    um = UserMetricsManager()
    tm = TimedMetricsManager()
    now = datetime.datetime.now()
    for doc in um.all():
        # TODO: filter on inactive clients
        for activity in activities:
            key_last_date = 'last_%s_date' % (activity) 
            key_last_slot = 'last_%s_slot' % (activity) 
            last_animator_activity_date = doc[key_last_date] if key_last_date in doc else None
            last_animator_activity_slot = doc[key_last_slot] if key_last_slot in doc else None
            
            if last_animator_activity_slot is None or last_animator_activity_date is None:
                continue
            
            days = 0
            if last_animator_activity_date:
                diff = (now - last_animator_activity_date)
                days = diff.days
    
            slot = tm.slot(days)
            
            if last_animator_activity_slot != slot:
                tm.inc_value(last_animator_activity_slot, activity, -1)
                tm.inc_value(slot, activity, 1)
    
@task(ignore_result=True)        
def async_check_if_new_listener(user_id):
    """
    Check if it is the first listening time for the user
    """
    uh = UserHistory()
    docs = uh.history_for_user(user_id, infinite=True, etype=UserHistory.ETYPE_LISTEN_RADIO)
    if docs is None or docs.count() == 0:
        async_inc_global_value('new_listeners', 1)
        