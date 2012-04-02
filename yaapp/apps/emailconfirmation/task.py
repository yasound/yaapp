from celery.task import task
from models import EmailConfirmation

        
@task
def resend_confirmations_task():
    EmailConfirmation.objects.resend_confirmations()
    
@task
def delete_expired_confirmations_task():
    EmailConfirmation.objects.delete_expired_confirmations()