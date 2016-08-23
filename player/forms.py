from django import forms

class SearchForm(forms.Form):
    artist_input = forms.CharField(label="Artist name", max_length=50)
    album_input = forms.CharField(label="Album name", max_length=50)
    