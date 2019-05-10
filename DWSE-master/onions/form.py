from django import forms
from .models import OnionSites


class PostForm(forms.ModelForm):
	class Meta :
		model = OnionSites
		fields = ('name','body',)