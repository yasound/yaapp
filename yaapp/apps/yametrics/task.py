from celery.task import task

@task(ignore_result=True)
def async_inc_global_value(key, value):  
    from models import GlobalMetricsManager
    mm = GlobalMetricsManager()
    mm.inc_global_value(key, value)


@task
def calculate_top_missing_songs_task():
    from models import TopMissingSongsManager
    tm = TopMissingSongsManager()
    tm.calculate()
        