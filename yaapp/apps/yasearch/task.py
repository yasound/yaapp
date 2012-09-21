from celery.task import task
import models
from indexer import add_radio, remove_radio
from yacore.database import flush_transaction

from yabase.models import Radio

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

@task(ignore_result=True)
def async_add_radio(radio_id):
    try:
        radio = Radio.objects.get(id=radio_id)
    except:
        return
    add_radio(radio, upsert=True, insert=False)

@task(ignore_result=True)
def async_remove_radio(radio):
    remove_radio(radio)