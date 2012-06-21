from celery.task import task

@task(ignore_result=True)
def async_add_radio(radio):
    from models import ClassifiedRadiosManager
    cm = ClassifiedRadiosManager()
    cm.add_radio(radio)
