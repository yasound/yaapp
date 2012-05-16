from django import forms
from django.utils.translation import ugettext_lazy as _
from models import Radio

def get_genres():
    genres = Radio.objects.all().values_list('genre', flat=True).distinct()
    items = [(x, x) for x in genres]
    items.insert(0, ('', '----------')) 
    return items

class SelectionForm(forms.Form):
    genre =  forms.ChoiceField(label=_('Genre'), choices=get_genres(),
                               required=False,
                               widget=forms.Select(attrs={"placeHolder": _('Genre')}))

class SettingsRadioForm(forms.ModelForm):
    genre =  forms.ChoiceField(label=_('Genre'), choices=get_genres(),
                               required=False,
                               widget=forms.Select(attrs={"placeHolder": _('Genre')}))
    class Meta:
        model = Radio
        fields = ('name', 'genre', 'picture', 'description', 'tags')    