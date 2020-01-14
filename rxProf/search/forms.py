from django import forms

class SearchForm(forms.Form):
	searchterm = forms.CharField(label="", required=False)
	
