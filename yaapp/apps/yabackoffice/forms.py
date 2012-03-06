from django import forms
from django.utils.translation import ugettext as _

import extjs
from yabase.models import Radio

class RadioForm(forms.ModelForm):
    class Meta:
        model = Radio
        fields = ['id', 'name',]
extjs.register(RadioForm)
