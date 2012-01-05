from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import post_save
from tastypie.models import create_api_key
from tastypie.models import ApiKey
from yabase.models import Radio
import yaapp.settings as yaapp_settings

class UserProfile(models.Model):
    user = models.OneToOneField(User, verbose_name=_('user'))
    name = models.CharField(max_length = 60, blank=True)
    url = models.URLField(null=True, blank=True)
    account_type = models.CharField(max_length=20, default='yasound')
    twitter_uid = models.CharField(max_length=60, null=True, blank=True)
    facebook_uid = models.CharField(max_length=60, null=True, blank=True)
    twitter_token = models.CharField(max_length=256, blank=True)
    twitter_token_secret = models.CharField(max_length=256, blank=True)
    facebook_token = models.CharField(max_length=256, blank=True)
    bio_text = models.TextField(null=True, blank=True)
    picture = models.ImageField(upload_to=yaapp_settings.PICTURE_FOLDER, null=True, blank=True)
    email_confirmed = models.BooleanField(default=False)
#    friends = models.ManyToManyField(User, related_name='friends_profile', null=True, blank=True)
    
    def __unicode__(self):
        return self.user.username
    
    def fill_user_bundle(self, bundle):
        picture_url = None
        if self.picture:
            picture_url = self.picture.url
        bundle.data['picture'] = picture_url
        bundle.data['bio_text'] = self.bio_text
        bundle.data['name'] = self.name
        
    def update_with_bundle(self, bundle, created):
        if bundle.data.has_key('bio_text'):
            self.bio_text = bundle.data['bio_text']
        if bundle.data.has_key('facebook_uid'):
            self.facebook_uid = bundle.data['facebook_uid']
        if bundle.data.has_key('twitter_uid'):
            self.twitter_uid = bundle.data['twitter_uid']
        if bundle.data.has_key('facebook_token'):
            self.facebook_token = bundle.data['facebook_token']
        if bundle.data.has_key('twitter_token'):
            self.twitter_token = bundle.data['twitter_token']
        if bundle.data.has_key('name'):
            self.name = bundle.data['name']
            
        if created and bundle.data.has_key('account_type'):
            t = bundle.data['account_type']
            self.account_type = t
            if  t == 'yasound':
                print 'new yasound user'
            elif t == 'facebook':
                print 'new facebook user'
            elif t == 'twitter':
                print 'new twitter user'
        self.save()

def create_user_profile(sender, instance, created, **kwargs):  
    if created:  
        profile, created = UserProfile.objects.get_or_create(user=instance)  

def create_radio(sender, instance, created, **kwargs):  
    if created:  
        radio, created = Radio.objects.get_or_create(creator=instance)

post_save.connect(create_user_profile, sender=User)
post_save.connect(create_api_key, sender=User)
post_save.connect(create_radio, sender=User)









