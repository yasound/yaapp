from celery.task import task
import models
from django.conf import settings

from yabase.utils import flush_transaction

@task
def build_mongodb_index():
    # avoid stale data        
    flush_transaction()
    models.build_mongodb_index(upsert=False, erase=False)
