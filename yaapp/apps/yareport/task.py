from celery.task import task
from models import report_song

@task
def task_report_song(radio, song_instance, play_datetime, report_datetime):
    report_song(radio, song_instance, play_datetime, report_datetime)