from celery.task import task
import models
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
def async_add_or_update_radio(radio_id):
    try:
        radio = Radio.objects.get(id=radio_id)
    except:
        return
    if not radio.ready or radio.deleted:
        radio.remove_from_fuzzy_index()
    else:
        radio.build_fuzzy_index(upsert=True, insert=False)

@task(ignore_result=True)
def async_update_radio_current_song(radio_id, song_dict):
    from models import RadiosManager
    rm = RadiosManager()
    rm.update_radio_current_song(radio_id, song_dict)


@task(ignore_result=True)
def async_remove_radio(radio):
    radio.remove_from_fuzzy_index()
