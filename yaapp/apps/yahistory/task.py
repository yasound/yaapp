from celery.task import task

# async stuff
@task(ignore_result=True)
def async_add_listen_radio_event(user_id, radio_uuid):
    from yahistory.models import UserHistory
    uh = UserHistory()
    uh.add_listen_radio_event(user_id, radio_uuid)

@task(ignore_result=True)
def async_add_post_message_event(user_id, radio_uuid, message):
    from yahistory.models import UserHistory
    uh = UserHistory()
    uh.add_post_message_event(user_id, radio_uuid, message)

@task(ignore_result=True)
def async_add_like_song_event(user_id, radio_uuid, song_id):
    from yahistory.models import UserHistory
    uh = UserHistory()
    uh.add_like_song_event(user_id, song_id)
