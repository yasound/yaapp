from celery.task import task
import models
from django.conf import settings

from yacore.database import flush_transaction

@task
def build_mongodb_index():
    # avoid stale data        
    flush_transaction()
    models.build_mongodb_index(upsert=False, erase=False)


@task(ignore_result=True)
def async_add_song(song_instance):
    from models import MostPopularSongsManager
    manager = MostPopularSongsManager()
    manager.add_song(song_instance)

@task(ignore_result=True)
def async_remove_song(metadata):
    from models import MostPopularSongsManager
    manager = MostPopularSongsManager()
    manager.remove_song(metadata)
    