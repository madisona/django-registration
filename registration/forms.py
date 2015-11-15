
from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string

from registration.models import RegistrationProfile


class ActivateUserMixin(object):
    """
    Prepares and send the activation email user's receive to complete their account setup.
    """
    activation_subject_template_name = "registration/email/activation_email_subject.txt"
    activation_template_name = "registration/email/activation_email.txt"
    activation_html_template_name = "registration/email/activation_email.html"

    def create_inactive_user(self, site, send_email=True):
        """
        Creates the inactive user and sends activation email. Only call when form is valid.
        """
        self.user = RegistrationProfile.objects.create_inactive_user(
            self.cleaned_data['username'],
            self.cleaned_data['password1'],
            self.cleaned_data['email'],
            site
        )
        if send_email:
            self.send_activation_email(self.user, site)
        return self.user

    def send_activation_email(self, user, current_site):
        mail_kwargs = {}
        subject = self._get_activation_subject(current_site)
        message = self._get_activation_message(current_site, self.activation_template_name)

        if self.activation_html_template_name:
            mail_kwargs['html_message'] = self._get_activation_message(current_site, self.activation_html_template_name)

        user.email_user(subject, message, settings.DEFAULT_FROM_EMAIL, **mail_kwargs)

    def _get_activation_subject(self, site):
        subject = render_to_string(self.activation_subject_template_name, {'site': site})
        return ''.join(subject.splitlines())

    def _get_activation_message(self, site, template_name):
        return render_to_string(template_name, self.get_email_context(site))

    def get_email_context(self, site):
        return {
            'site': site,
            'activation_key': self.user.registrationprofile.activation_key,
            'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS,
        }


class RegistrationForm(ActivateUserMixin, forms.Form):
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
            user_model.objects.get(**{username_lookup: self.cleaned_data['username']})
        except user_model.DoesNotExist:
            return self.cleaned_data['username']
        raise forms.ValidationError("Username '%(username)s' is not available." % self.cleaned_data)

    def clean(self):
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError("Passwords must match.")

        return self.cleaned_data
