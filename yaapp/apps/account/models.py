from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import post_save
from tastypie.models import create_api_key
from tastypie.models import ApiKey
from yabase.models import Radio

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
    
    def fill_user_bundle(self, bundle):
        p = None
        if self.picture:
            p = '/media/' + unicode(self.picture)
        bundle.data['picture'] = p
        bundle.data['bio_text'] = self.bio_text
        bundle.data['facebook_account'] = self.facebook_account
        bundle.data['twitter_account'] = self.twitter_account
        bundle.data['url'] = self.url

def create_user_profile(sender, instance, created, **kwargs):  
    if created:  
        profile, created = UserProfile.objects.get_or_create(user=instance)
        
def create_radio(sender, instance, created, **kwargs):  
    if created:  
        radio_name = instance.username + "'s radio"
        print radio_name
        radio, created = Radio.objects.get_or_create(creator=instance, name=radio_name)
          

post_save.connect(create_user_profile, sender=User)
post_save.connect(create_api_key, sender=User)
post_save.connect(create_radio, sender=User)


#for user in User.objects.all(): 
#    ApiKey.objects.get_or_create(user=user)








