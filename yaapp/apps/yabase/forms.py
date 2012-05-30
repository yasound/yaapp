from account.models import UserProfile
from bootstrap.forms import BootstrapModelForm, Fieldset, BootstrapForm
from django import forms
from django.utils.translation import ugettext_lazy as _
from models import Radio


class SettingsRadioForm(BootstrapModelForm):
    class Meta:
        model = Radio
        fields = ('name', 'genre', 'picture', 'description', 'tags')
        layout = (
            Fieldset(_('My radio'), 'name', 'genre', 'picture', 'description', 'tags'),
        )

class SettingsUserForm(BootstrapModelForm):
    class Meta:
        model = UserProfile
        fields = ('name', 'bio_text', 'picture')
        layout = (
            Fieldset(_('Profile'), 'name', 'bio_text', 'picture'),
        )

class SettingsFacebookForm(BootstrapForm):
    fb_share_listen = forms.BooleanField(label=_("Listen"), required=False)
    fb_share_like_song = forms.BooleanField(label=_("Like song"), required=False)
    fb_share_post_message = forms.BooleanField(label=_("Post message"), required=False)
    class Meta:
        layout = (
            Fieldset(_('Facebook share options'), 
                     'fb_share_listen', 
                     'fb_share_like_song', 
                     'fb_share_post_message'),
        )
        
    def __init__(self, user_profile=None, *args, **kwargs):
        self.user_profile = user_profile
        initial = {
            'fb_share_listen': self.user_profile.notifications_preferences.fb_share_listen,
            'fb_share_like_song': self.user_profile.notifications_preferences.fb_share_like_song,
            'fb_share_post_message': self.user_profile.notifications_preferences.fb_share_post_message,
        }
        super(SettingsFacebookForm, self).__init__(initial=initial, *args, **kwargs)
        
    def save(self):
        fb_share_listen = self.cleaned_data['fb_share_listen']
        fb_share_like_song = self.cleaned_data['fb_share_like_song']
        fb_share_post_message = self.cleaned_data['fb_share_post_message']
        
        self.user_profile.notifications_preferences.fb_share_listen = fb_share_listen
        self.user_profile.notifications_preferences.fb_share_like_song = fb_share_like_song
        self.user_profile.notifications_preferences.fb_share_post_message = fb_share_post_message
        
        self.user_profile.save()