from account.models import UserProfile
from bootstrap.forms import BootstrapModelForm, Fieldset, BootstrapForm
from django import forms
from django.utils.translation import ugettext_lazy as _
from models import Radio
from yabase.task import async_import_from_itunes
from yacore.tags import clean_tags
import logging
import settings as yabase_settings
from taggit.forms import TagField
logger = logging.getLogger("yaapp.yabase")

class SettingsRadioForm(BootstrapModelForm):
    tags = TagField(label=_('Tags'), help_text=_('A comma-separated list of tags'), required=False)

    class Meta:
        model = Radio
        fields = ('name', 'genre', 'description', 'tags')
        layout = (
            Fieldset('', 'name', 'genre', 'description', 'tags'),
        )

    def clean_tags(self):
        tags = self.cleaned_data['tags']
        tags = clean_tags(tags)
        self.cleaned_data['tags'] = tags
        return tags


class MyInformationsForm(BootstrapModelForm):
    bio_text = forms.CharField(label=_('Biography'), widget=forms.widgets.Textarea(attrs={'rows':5, 'cols':60}))
    class Meta:
        model = UserProfile
        fields = ('name', 'url', 'bio_text', 'birthday', 'gender', 'city')
        layout = (
            Fieldset('', 'name', 'url', 'bio_text', 'birthday', 'gender', 'city'),
        )

class MyAccountsForm(BootstrapModelForm):
    password1 = forms.CharField(label=_("Password"), required=False, widget=forms.PasswordInput())
    password2 = forms.CharField(label=_("Password (again)"), required=False, widget=forms.PasswordInput())

    class Meta:
        model = UserProfile
        fields = ('yasound_email',)
        layout = (
            Fieldset('Yasound', 'yasound_email', 'password1', 'password2'),
        )

    def clean(self):
        if "password1" in self.cleaned_data and "password2" in self.cleaned_data:
            if self.cleaned_data["password1"] != self.cleaned_data["password2"]:
                raise forms.ValidationError(u"You must type the same password each time.")

        if 'remove_facebook' in self.data:
            success, message = self.instance.remove_facebook_account()
            if not success:
                raise forms.ValidationError(message)

        if 'remove_twitter' in self.data:
            success, message = self.instance.remove_twitter_account()
            if not success:
                raise forms.ValidationError(message)

        return self.cleaned_data

    def save(self):
        if "password1" in self.cleaned_data:
            self.instance.user.set_password(self.cleaned_data['password1'])
            self.instance.user.save()

class MyNotificationsForm(BootstrapForm):
    fb_share_listen = forms.BooleanField(label=_("Listen"), required=False)
    fb_share_like_song = forms.BooleanField(label=_("Like song"), required=False)
    fb_share_post_message = forms.BooleanField(label=_("Post message"), required=False)
    fb_share_animator_activity = forms.BooleanField(label=_("Update programming"), required=False)

    tw_share_listen = forms.BooleanField(label=_("Listen"), required=False)
    tw_share_like_song = forms.BooleanField(label=_("Like song"), required=False)
    tw_share_post_message = forms.BooleanField(label=_("Post message"), required=False)
    tw_share_animator_activity = forms.BooleanField(label=_("Update programming"), required=False)

    user_in_radio = forms.BooleanField(label=_("A user enters"), required=False)
    friend_in_radio = forms.BooleanField(label=_("A friend enters"), required=False)
    friend_online = forms.BooleanField(label=_("A friend goes online"), required=False)
    message_posted = forms.BooleanField(label=_("A message is posted"), required=False)
    song_liked = forms.BooleanField(label=_("Someone likes a song"), required=False)
    radio_in_favorites = forms.BooleanField(label=_("My radio is added as favorite"), required=False)
    radio_shared = forms.BooleanField(label=_("Someone shared my radio"), required=False)
    friend_created_radio = forms.BooleanField(label=_("A friend creates his radio"), required=False)

    FIELDSET_FACEBOOK = 1
    FIELDSET_TWITTER = 2
    class Meta:
        layout = (
            Fieldset(_('Notifications'),
                    'user_in_radio',
                    'friend_in_radio',
                    'friend_online',
                    'message_posted',
                    'song_liked',
                    'radio_in_favorites',
                    'radio_shared',
                    'friend_created_radio'),

            Fieldset(_('Facebook share options'),
                     'fb_share_listen',
                     'fb_share_like_song',
                     'fb_share_post_message',
                     'fb_share_animator_activity'),

            Fieldset(_('Twitter share options'),
                     'tw_share_listen',
                     'tw_share_like_song',
                     'tw_share_post_message',
                     'tw_share_animator_activity'),
        )

    def __init__(self, user_profile=None, *args, **kwargs):
        from django.forms.widgets import HiddenInput

        self.user_profile = user_profile
        initial = {
            'fb_share_listen': self.user_profile.notifications_preferences.fb_share_listen,
            'fb_share_like_song': self.user_profile.notifications_preferences.fb_share_like_song,
            'fb_share_post_message': self.user_profile.notifications_preferences.fb_share_post_message,
            'fb_share_animator_activity': self.user_profile.notifications_preferences.fb_share_animator_activity,
            'tw_share_listen': self.user_profile.notifications_preferences.tw_share_listen,
            'tw_share_like_song': self.user_profile.notifications_preferences.tw_share_like_song,
            'tw_share_post_message': self.user_profile.notifications_preferences.tw_share_post_message,
            'tw_share_animator_activity': self.user_profile.notifications_preferences.tw_share_animator_activity,
            'user_in_radio': self.user_profile.notifications_preferences.user_in_radio,
            'friend_in_radio': self.user_profile.notifications_preferences.friend_in_radio,
            'friend_online': self.user_profile.notifications_preferences.friend_online,
            'message_posted': self.user_profile.notifications_preferences.message_posted,
            'song_liked': self.user_profile.notifications_preferences.song_liked,
            'radio_in_favorites': self.user_profile.notifications_preferences.radio_in_favorites,
            'radio_shared': self.user_profile.notifications_preferences.radio_shared,
            'friend_created_radio': self.user_profile.notifications_preferences.friend_created_radio,
        }

        super(MyNotificationsForm, self).__init__(initial=initial, *args, **kwargs)

        self.Meta.layout[MyNotificationsForm.FIELDSET_FACEBOOK].css_class='facebook_share_options'
        self.Meta.layout[MyNotificationsForm.FIELDSET_TWITTER].css_class='twitter_share_options'

        if not self.user_profile.facebook_enabled:
            # hide facebook related fields
            names = ['fb_share_listen',
                     'fb_share_like_song',
                     'fb_share_post_message',
                     'fb_share_animator_activity']
            for name in names:
                self.fields[name].widget = HiddenInput()
            self.Meta.layout[MyNotificationsForm.FIELDSET_FACEBOOK].css_class = 'hidden-display'

        if not self.user_profile.twitter_enabled:
            # hide twitter related fields
            names = ['tw_share_listen',
                     'tw_share_like_song',
                     'tw_share_post_message',
                     'tw_share_animator_activity']
            for name in names:
                self.fields[name].widget = HiddenInput()
            self.Meta.layout[MyNotificationsForm.FIELDSET_TWITTER].css_class = 'hidden-display'


    def save(self):

        fb_share_listen = self.cleaned_data['fb_share_listen']
        fb_share_like_song = self.cleaned_data['fb_share_like_song']
        fb_share_post_message = self.cleaned_data['fb_share_post_message']
        fb_share_animator_activity = self.cleaned_data['fb_share_animator_activity']

        self.user_profile.notifications_preferences.fb_share_listen = fb_share_listen
        self.user_profile.notifications_preferences.fb_share_like_song = fb_share_like_song
        self.user_profile.notifications_preferences.fb_share_post_message = fb_share_post_message
        self.user_profile.notifications_preferences.fb_share_animator_activity = fb_share_animator_activity

        tw_share_listen = self.cleaned_data['tw_share_listen']
        tw_share_like_song = self.cleaned_data['tw_share_like_song']
        tw_share_post_message = self.cleaned_data['tw_share_post_message']
        tw_share_animator_activity = self.cleaned_data['tw_share_animator_activity']

        self.user_profile.notifications_preferences.tw_share_listen = tw_share_listen
        self.user_profile.notifications_preferences.tw_share_like_song = tw_share_like_song
        self.user_profile.notifications_preferences.tw_share_post_message = tw_share_post_message
        self.user_profile.notifications_preferences.tw_share_animator_activity = tw_share_animator_activity

        user_in_radio = self.cleaned_data['user_in_radio']
        friend_in_radio = self.cleaned_data['friend_in_radio']
        friend_online = self.cleaned_data['friend_online']
        message_posted = self.cleaned_data['message_posted']
        song_liked = self.cleaned_data['song_liked']
        radio_in_favorites = self.cleaned_data['radio_in_favorites']
        radio_shared = self.cleaned_data['radio_shared']
        friend_created_radio = self.cleaned_data['friend_created_radio']

        self.user_profile.notifications_preferences.user_in_radio = user_in_radio
        self.user_profile.notifications_preferences.friend_in_radio = friend_in_radio
        self.user_profile.notifications_preferences.friend_online = friend_online
        self.user_profile.notifications_preferences.message_posted = message_posted
        self.user_profile.notifications_preferences.song_liked = song_liked
        self.user_profile.notifications_preferences.radio_in_favorites = radio_in_favorites
        self.user_profile.notifications_preferences.radio_shared = radio_shared
        self.user_profile.notifications_preferences.friend_created_radio = friend_created_radio

        self.user_profile.save()


class SettingsUserForm(BootstrapModelForm):
    password1 = forms.CharField(label=_("Password"), required=False, widget=forms.PasswordInput())
    password2 = forms.CharField(label=_("Password (again)"), required=False, widget=forms.PasswordInput())

    class Meta:
        model = UserProfile
        fields = ('name', 'bio_text', 'picture', 'yasound_email')
        layout = (
            Fieldset('', 'name', 'bio_text', 'picture', 'yasound_email', 'password1', 'password2'),
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
    tw_share_listen = forms.BooleanField(label=_("Listen"), required=False)
    tw_share_like_song = forms.BooleanField(label=_("Like song"), required=False)
    tw_share_post_message = forms.BooleanField(label=_("Post message"), required=False)
    tw_share_animator_activity = forms.BooleanField(label=_("Update programming"), required=False)
    class Meta:
        layout = (
            Fieldset(_('Twitter share options'),
                     'tw_share_listen',
                     'tw_share_like_song',
                     'tw_share_post_message',
                     'tw_share_animator_activity'),
        )

    def __init__(self, user_profile=None, *args, **kwargs):
        self.user_profile = user_profile
        initial = {
            'tw_share_listen': self.user_profile.notifications_preferences.tw_share_listen,
            'tw_share_like_song': self.user_profile.notifications_preferences.tw_share_like_song,
            'tw_share_post_message': self.user_profile.notifications_preferences.tw_share_post_message,
            'tw_share_animator_activity': self.user_profile.notifications_preferences.tw_share_animator_activity,
        }
        super(SettingsTwitterForm, self).__init__(initial=initial, *args, **kwargs)

    def clean(self):
        if 'remove' in self.data:
            success, message = self.user_profile.remove_twitter_account()
            if not success:
                raise forms.ValidationError(message)

        return self.cleaned_data


    def save(self):
        tw_share_listen = self.cleaned_data['tw_share_listen']
        tw_share_like_song = self.cleaned_data['tw_share_like_song']
        tw_share_post_message = self.cleaned_data['tw_share_post_message']
        tw_share_animator_activity = self.cleaned_data['tw_share_animator_activity']

        self.user_profile.notifications_preferences.tw_share_listen = tw_share_listen
        self.user_profile.notifications_preferences.tw_share_like_song = tw_share_like_song
        self.user_profile.notifications_preferences.tw_share_post_message = tw_share_post_message
        self.user_profile.notifications_preferences.tw_share_animator_activity = tw_share_animator_activity

        self.user_profile.save()

class ImportItunesForm(BootstrapForm):
    uuid = forms.CharField(required=True)
    tracks = forms.CharField(label=_('Please paste from iTunes'),
                             widget=forms.Textarea,
                                    required=True)
    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        super(ImportItunesForm, self).__init__(initial={}, *args, **kwargs)

    def save(self):
        tracks = self.cleaned_data['tracks']
        uuid = self.cleaned_data['uuid']
        radio = Radio.objects.get(uuid=uuid)
        if radio.creator == self.user:
            async_import_from_itunes.delay(radio=radio, data=tracks)

class RadioGenreForm(forms.Form):
    genre = forms.ChoiceField(choices = yabase_settings.RADIO_STYLE_CHOICES_FORM, required=False)
