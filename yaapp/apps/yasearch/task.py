from celery.task import task
import models

@task
def build_mongodb_index():
    models.build_mongodb_index(upsert=False, erase=False)

