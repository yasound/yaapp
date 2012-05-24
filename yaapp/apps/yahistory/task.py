from celery.decorators import task

# async stuff
@task(ignore_result=True)
def async_add_listen_radio_event(user_id, radio_uuid):
    from yahistory.models import UserHistory
    uh = UserHistory()
    uh.add_listen_radio_event(user_id, radio_uuid)
