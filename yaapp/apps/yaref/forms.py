from django import forms

class SearchForm(forms.Form):
    song = forms.CharField(max_length=255, required=False)
    album = forms.CharField(max_length=255, required=False)
    artist = forms.CharField(max_length=255, required=False)
