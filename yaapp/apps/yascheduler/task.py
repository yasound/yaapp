from celery.task import task


@task(ignore_result=True)
def async_transient_radio_event(event_type, radio_uuid, playlist_id=None, jingle_id=None):
    from models import TransientRadioHistoryManager
    tr = TransientRadioHistoryManager()
    tr.add_event(event_type=event_type, radio_uuid=radio_uuid, playlist_id=playlist_id, jingle_id=jingle_id)
