
from django import forms

class RegistrationForm(forms.Form):
    username = forms.RegexField(regex=r'^\w+$', max_length=30,
                                error_messages={'invalid': 'This value must contain only letters, numbers, and underscores.'})
    email = forms.EmailField(max_length=75)
    password1 = forms.CharField(widget=forms.PasswordInput())
    password2 = forms.CharField(widget=forms.PasswordInput())