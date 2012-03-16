from celery.task import task
from models import report_song

@task
def task_report_song(radio, song_instance):
    report_song(radio, song_instance)