from celery.task import task

# async stuff


@task(ignore_result=True)
def async_add_listen_radio_event(user_id, radio_uuid):
    from yahistory.models import UserHistory
    uh = UserHistory()
    uh.add_listen_radio_event(user_id, radio_uuid)


@task(ignore_result=True)
def async_add_watch_tutorial_event(user_id):
    from yahistory.models import UserHistory
    uh = UserHistory()
    uh.add_watch_tutorial_event(user_id)


@task(ignore_result=True)
def async_add_post_message_event(user_id, radio_uuid, message):
    from yahistory.models import UserHistory
    uh = UserHistory()
    uh.add_post_message_event(user_id, radio_uuid, message)


@task(ignore_result=True)
def async_add_like_song_event(user_id, radio_uuid, song_id):
    from yahistory.models import UserHistory
    uh = UserHistory()
    uh.add_like_song_event(user_id, radio_uuid, song_id)


@task(ignore_result=True)
def async_add_favorite_radio_event(user_id, radio_uuid):
    from yahistory.models import UserHistory
    uh = UserHistory()
    uh.add_favorite_radio_event(user_id, radio_uuid)


@task(ignore_result=True)
def async_add_not_favorite_radio_event(user_id, radio_uuid):
    from yahistory.models import UserHistory
    uh = UserHistory()
    uh.add_not_favorite_radio_event(user_id, radio_uuid)


@task(ignore_result=True)
def async_add_share_event(user_id, radio_uuid, share_type):
    from yahistory.models import UserHistory
    uh = UserHistory()
    uh.add_share_event(user_id, radio_uuid, share_type)


@task(ignore_result=True)
def async_add_animator_event(user_id, radio_uuid, atype, details):
    from yahistory.models import UserHistory
    uh = UserHistory()
    uh.add_animator_event(user_id, radio_uuid, atype, details)


@task(ignore_result=True)
def async_add_buy_link_event(user_id, radio_uuid, song_id):
    from yahistory.models import UserHistory
    uh = UserHistory()
    uh.add_buy_link_event(user_id, radio_uuid, song_id)
