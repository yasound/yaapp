from account.models import UserProfile
from celery.task import task
from django.core.urlresolvers import reverse
from facepy import GraphAPI
from yacore.http import absolute_url
from django.conf import settings

def _facebook_token(user_id):
    try:
        user_profile = UserProfile.objects.get(user__id=user_id)
    except:
        return None
    
    if not user_profile.facebook_enabled or len(user_profile.facebook_token) <= 0:
        return None
    facebook_token = user_profile.facebook_token
    return facebook_token

@task(ignore_result=True)
def async_post_message(user_id, radio_uuid, message):
    facebook_token = _facebook_token(user_id)
    if facebook_token is None:
        return
    
    radio_url = absolute_url(reverse('webapp_radio', args=[radio_uuid])) 
    data = {
       'radio':radio_url
    }
    path = 'me/%s:post_message' % (settings.FACEBOOK_APP_NAMESPACE)

    graph = GraphAPI(facebook_token)
    graph.post(path=path, data=data)
    
@task(ignore_result=True)
def async_listen(user_id, radio_uuid, song_title):
    facebook_token = _facebook_token(user_id)
    if facebook_token is None:
        return

    radio_url = absolute_url(reverse('webapp_radio', args=[radio_uuid])) 
    data = {
       'radio':radio_url,
       'song': song_title
    }
    path = 'me/%s:listen' % (settings.FACEBOOK_APP_NAMESPACE)

    graph = GraphAPI(facebook_token)
    graph.post(path=path, data=data)

@task(ignore_result=True)
def async_like_song(user_id, radio_uuid, song_title):
    facebook_token = _facebook_token(user_id)
    if facebook_token is None:
        return

    radio_url = absolute_url(reverse('webapp_radio', args=[radio_uuid])) 
    data = {
       'radio':radio_url,
       'song': song_title
    }
    path = 'me/%s:like' % (settings.FACEBOOK_APP_NAMESPACE)

    graph = GraphAPI(facebook_token)
    graph.post(path=path, data=data)
