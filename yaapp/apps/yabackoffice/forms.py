from django import forms
from django.utils.translation import ugettext as _
from yabase.models import Radio
from yainvitation.models import Invitation
import extjs


class RadioForm(forms.ModelForm):
    class Meta:
        model = Radio
        fields = ['id', 'name',]
extjs.register(RadioForm)

class InvitationForm(forms.ModelForm):
    class Meta:
        model = Invitation
        fields = ['id', 'fullname',]
extjs.register(InvitationForm)
