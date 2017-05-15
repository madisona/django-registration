from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.template import RequestContext

from registration import get_site
from registration.models import RegistrationProfile


class ActivateUserMixin(object):
    """
    Prepares and send the activation email user's receive to
    complete their account setup.
    """
    activation_subject_template_name = "registration/email/activation_email_subject.txt"  # noqa: E501
    activation_template_name = "registration/email/activation_email.txt"
    activation_html_template_name = "registration/email/activation_email.html"

    def _get_user_username(self):
        return self.cleaned_data['username']

    def _get_user_email(self):
        return self.cleaned_data['email']

    def _get_user_password(self):
        return self.cleaned_data['password1']

    def create_inactive_user(self, request=None, send_email=True):
        """
        Creates the inactive user and sends activation email. Only call
        when form is valid. Request object is for RequestContext and current
        site to send to templates.
        """
        self.user = RegistrationProfile.objects.create_inactive_user(
            self._get_user_username(),
            self._get_user_password(),
            self._get_user_email(), )
        if send_email:
            self.request = request
            self.send_activation_email(self.user)
        return self.user

    def send_activation_email(self, user):
        current_site = get_site(self.request)

        mail_kwargs = {}
        subject = self._get_activation_subject(current_site)
        message = self._get_activation_message(current_site,
                                               self.activation_template_name)

        if self.activation_html_template_name:
            mail_kwargs['html_message'] = self._get_activation_message(
                current_site, self.activation_html_template_name)

        user.email_user(subject, message, settings.DEFAULT_FROM_EMAIL,
                        **mail_kwargs)

    def _get_activation_subject(self, site):
        subject = render_to_string(
            self.activation_subject_template_name, {'site': site},
            RequestContext(self.request))
        return ''.join(subject.splitlines())

    def _get_activation_message(self, site, template_name):
        return render_to_string(template_name,
                                self.get_email_context(site),
                                RequestContext(self.request))

    def _get_activation_url(self, activation_key):
        path = reverse(
            "registration_activate", kwargs={"activation_key": activation_key})
        return "{protocol}://{host}{path}".format(
            protocol="https" if self.request.is_secure() else "http",
            host=self.request.get_host(),
            path=path, )

    def get_email_context(self, site):
        activation_key = self.user.registrationprofile.activation_key
        return dict({
            'site':
            site,
            'activation_key':
            activation_key,
            'activation_url':
            self._get_activation_url(activation_key),
            'expiration_days':
            settings.ACCOUNT_ACTIVATION_DAYS,
        }, **self.cleaned_data)


class RegistrationForm(ActivateUserMixin, forms.Form):
    username = forms.RegexField(
        regex=r'^[\w.@+-]+$',
        max_length=30,
        error_messages={
            'invalid':
            'Enter a valid username. '
            'This value may contain only letters, numbers '
            'and @/./+/-/_ characters.'
        })
    email = forms.EmailField(max_length=75)
    password1 = forms.CharField(widget=forms.PasswordInput())
    password2 = forms.CharField(widget=forms.PasswordInput())

    def clean_username(self):
        user_model = get_user_model()
        try:
            username_lookup = "{}__iexact".format(user_model.USERNAME_FIELD)
            user_model.objects.get(
                **{username_lookup: self.cleaned_data['username']})
        except user_model.DoesNotExist:
            return self.cleaned_data['username']
        raise forms.ValidationError(
            "Username '%(username)s' is not available." % self.cleaned_data)

    def clean(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 is not None and password2 is not None \
                and password1 != password2:
            raise forms.ValidationError("Passwords must match.")

        return self.cleaned_data
