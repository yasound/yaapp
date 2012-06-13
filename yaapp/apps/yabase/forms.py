from account.models import UserProfile
from bootstrap.forms import BootstrapModelForm, Fieldset, BootstrapForm
from django import forms
from django.utils.translation import ugettext_lazy as _
from import_utils import parse_itunes_line
from models import Radio
from yacore.tags import clean_tags
import logging
logger = logging.getLogger("yaapp.yabase")
from import_utils import import_from_string

class SettingsRadioForm(BootstrapModelForm):
    class Meta:
        model = Radio
        fields = ('name', 'genre', 'picture', 'description', 'tags')
        layout = (
            Fieldset(_('My radio'), 'name', 'genre', 'picture', 'description', 'tags'),
        )
    
    def clean_tags(self):
        tags = self.cleaned_data['tags']
        tags = clean_tags(tags)
        self.cleaned_data['tags'] = tags
        return tags

class SettingsUserForm(BootstrapModelForm):
    password1 = forms.CharField(label=_("Password"), required=False, widget=forms.PasswordInput())
    password2 = forms.CharField(label=_("Password (again)"), required=False, widget=forms.PasswordInput())

    class Meta:
        model = UserProfile
        fields = ('name', 'bio_text', 'picture', 'yasound_email')
        layout = (
            Fieldset(_('Profile'), 'name', 'bio_text', 'picture', 'yasound_email', 'password1', 'password2'),
        )
        
    def clean(self):
        if "password1" in self.cleaned_data and "password2" in self.cleaned_data:
            if self.cleaned_data["password1"] != self.cleaned_data["password2"]:
                raise forms.ValidationError(u"You must type the same password each time.")
            
        return self.cleaned_data
        

class SettingsFacebookForm(BootstrapForm):
    fb_share_listen = forms.BooleanField(label=_("Listen"), required=False)
    fb_share_like_song = forms.BooleanField(label=_("Like song"), required=False)
    fb_share_post_message = forms.BooleanField(label=_("Post message"), required=False)
    fb_share_animator_activity = forms.BooleanField(label=_("Update programming"), required=False)
    class Meta:
        layout = (
            Fieldset(_('Facebook share options'), 
                     'fb_share_listen', 
                     'fb_share_like_song', 
                     'fb_share_post_message',
                     'fb_share_animator_activity'),
        )
        
    def __init__(self, user_profile=None, *args, **kwargs):
        self.user_profile = user_profile
        initial = {
            'fb_share_listen': self.user_profile.notifications_preferences.fb_share_listen,
            'fb_share_like_song': self.user_profile.notifications_preferences.fb_share_like_song,
            'fb_share_post_message': self.user_profile.notifications_preferences.fb_share_post_message,
            'fb_share_animator_activity': self.user_profile.notifications_preferences.fb_share_animator_activity,
        }
        super(SettingsFacebookForm, self).__init__(initial=initial, *args, **kwargs)
        
    def clean(self):
        if 'remove' in self.data:
            success, message = self.user_profile.remove_facebook_account()
            if not success: 
                raise forms.ValidationError(message)

        return self.cleaned_data
       
    
    def save(self):
        
        fb_share_listen = self.cleaned_data['fb_share_listen']
        fb_share_like_song = self.cleaned_data['fb_share_like_song']
        fb_share_post_message = self.cleaned_data['fb_share_post_message']
        fb_share_animator_activity = self.cleaned_data['fb_share_animator_activity']
        
        self.user_profile.notifications_preferences.fb_share_listen = fb_share_listen
        self.user_profile.notifications_preferences.fb_share_like_song = fb_share_like_song
        self.user_profile.notifications_preferences.fb_share_post_message = fb_share_post_message
        self.user_profile.notifications_preferences.fb_share_animator_activity = fb_share_animator_activity
        
        self.user_profile.save()
        
class SettingsTwitterForm(BootstrapForm):
    class Meta:
        layout = (
            Fieldset(_('Twitter share options'), ),
        )

    def __init__(self, user_profile=None, *args, **kwargs):
        self.user_profile = user_profile
        initial = {
        }
        super(SettingsTwitterForm, self).__init__(initial=initial, *args, **kwargs)
        
    def clean(self):
        if 'remove' in self.data:
            success, message = self.user_profile.remove_twitter_account()
            if not success: 
                raise forms.ValidationError(message)

        return self.cleaned_data
       
    
    def save(self):
        pass
    
class ImportItunesForm(BootstrapForm):
    tracks = forms.CharField(label=_('Please paste from iTunes'), 
                             widget=forms.Textarea, 
                                    required=True)
    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        super(ImportItunesForm, self).__init__(initial={}, *args, **kwargs)

    def save(self):
        tracks = self.cleaned_data['tracks']
        lines = tracks.split('\n')
        for line in lines:
            name, album, artist = parse_itunes_line(line)
            logger.info('name=%s, album=%s, artist=%s' % (name, album, artist))
            if len(name) > 0:
                radio = Radio.objects.radio_for_user(self.user)
                playlist, _created = radio.get_or_create_default_playlist()
                import_from_string(name, album, artist, playlist)
