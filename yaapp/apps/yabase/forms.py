from account.models import UserProfile
from bootstrap.forms import BootstrapModelForm, Fieldset
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
    