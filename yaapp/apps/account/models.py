from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import post_save
from tastypie.models import create_api_key
from tastypie.models import ApiKey

class UserProfile(models.Model):
    user = models.OneToOneField(User, verbose_name=_('user'))
    url = models.URLField(null=True, blank=True)
    twitter_account = models.CharField(max_length=60, null=True, blank=True)
    facebook_account = models.CharField(max_length=60, null=True, blank=True)
    bio_text = models.TextField(null=True, blank=True)
    picture = models.ImageField(upload_to='pictures', null=True, blank=True)
#    friends = models.ManyToManyField(User, related_name='friends_profile', null=True, blank=True)
    
    def __unicode__(self):
        return self.user.username

def create_user_profile(sender, instance, created, **kwargs):  
    if created:  
        profile, created = UserProfile.objects.get_or_create(user=instance)  
post_save.connect(create_user_profile, sender=User)


post_save.connect(create_api_key, sender=User)

 
for user in User.objects.all(): 
    ApiKey.objects.get_or_create(user=user) 








