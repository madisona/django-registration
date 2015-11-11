
from django import forms
from django.contrib.auth import get_user_model


class RegistrationForm(forms.Form):
    username = forms.RegexField(regex=r'^[\w.@+-]+$', max_length=30,
                                error_messages={'invalid': 'Enter a valid username. '
                                                           'This value may contain only letters, numbers '
                                                           'and @/./+/-/_ characters.'})
    email = forms.EmailField(max_length=75)
    password1 = forms.CharField(widget=forms.PasswordInput())
    password2 = forms.CharField(widget=forms.PasswordInput())

    def clean_username(self):
        user_model = get_user_model()
        try:
            username_lookup = "{}__iexact".format(user_model.USERNAME_FIELD)
            _ = user_model.objects.get(**{username_lookup: self.cleaned_data['username']})
        except user_model.DoesNotExist:
            return self.cleaned_data['username']
        raise forms.ValidationError("Username '%(username)s' is not available." % self.cleaned_data)

    def clean(self):
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError("Passwords must match.")

        return self.cleaned_data
