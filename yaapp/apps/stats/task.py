from celery.task import task
from yabase.models import Radio

@task
def radio_listening_stats_task():
    print 'radio_listening_stats_task'
    radios = Radio.objects.all()
    for radio in radios:
        if radio.is_valid:
            radio.create_listening_stat()
            
    print 'radio_listening_stats_task DONE'