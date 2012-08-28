from celery.task import task
from models import UserService
from datetime import *


@task
def check_expiration_date():
    today = date.today()
    uss = UserService.objects.filter(expiration_date__lt=today, active=True)
    for us in uss:
        us.active = False
        us.save()
