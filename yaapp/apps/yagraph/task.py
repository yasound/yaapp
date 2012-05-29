from account.models import UserProfile
from celery.task import task
from django.core.urlresolvers import reverse
from facepy import GraphAPI
from yacore.http import absolute_url

@task(ignore_result=True)
def async_post_message(user_id, radio_uuid, message):
    try:
        user_profile = UserProfile.objects.get(user__id=user_id)
    except:
        return
    
    if not user_profile.facebook_enabled or len(user_profile.facebook_token) <= 0:
        return
    
    radio_url = absolute_url(reverse('webapp_radio', args=[radio_uuid])) 
    
    facebook_token = user_profile.facebook_token
    graph = GraphAPI(facebook_token)
    
    data = {
       'radio':radio_url
    }
    graph.post(path='me/yasoundev:post_a_message', data=data)