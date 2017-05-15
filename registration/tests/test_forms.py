from django import test
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import mail
from django.core.urlresolvers import reverse

from registration import forms
from registration import get_site


class RegistrationFormTests(test.TestCase):
    def test_requires_username_to_be_unique(self):
        get_user_model().objects.create_user("alice", "alice@example.com",
                                             "secret")
        registration_form = forms.RegistrationForm({
            "username":
            "alice",
            "email":
            "alice@example.com",
            "password1":
            "secret",
            "password2":
            "secret",
        })
        self.failIf(registration_form.is_valid())
        self.assertEqual(["Username 'alice' is not available."],
                         registration_form.errors['username'])

    def test_rejects_certain_characters_in_username(self):
        registration_form = forms.RegistrationForm({
            "username":
            "alice$",
            "email":
            "alice@example.com",
            "password1":
            "secret",
            "password2":
            "secret",
        })
        self.failIf(registration_form.is_valid())
        self.assertEqual([
            'Enter a valid username. '
            'This value may contain only letters, numbers '
            'and @/./+/-/_ characters.'
        ], registration_form.errors['username'])

    def test_allows_email_underscores_periods_and_plusses_in_username(
            self):
        registration_form = forms.RegistrationForm({
            "username":
            "al.ice+fun-tim_es@wond.er",
            "email":
            "alice@example.com",
            "password1":
            "secret",
            "password2":
            "secret",
        })
        self.assertEqual(True, registration_form.is_valid())

    def test_requires_passwords_to_match(self):
        registration_form = forms.RegistrationForm({
            "username":
            "alice",
            "email":
            "alice@example.com",
            "password1":
            "secret",
            "password2":
            "pswd",
        })
        self.failIf(registration_form.is_valid())
        self.assertEqual(["Passwords must match."],
                         registration_form.errors['__all__'])


class RegistrationActivateUserFormTests(test.TestCase):
    def setUp(self):
        self.sut = forms.RegistrationForm
        self.form_data = {
            "username": "user",
            "password1": "pswd",
            "password2": "pswd",
            "email": "test@example.com"
        }

    def test_creates_user_and_profile(self):
        request = test.RequestFactory().get("/")
        form = self.sut(data=self.form_data)
        form.is_valid()
        user = form.create_inactive_user(request, send_email=False)

        self.assertEqual(self.form_data['username'], user.username)
        self.assertEqual(self.form_data['email'], user.email)
        self.assertEqual(True,
                         user.check_password(self.form_data["password1"]))
        self.assertIsNotNone(user.registrationprofile.activation_key)

    def test_doesnt_send_email_if_requested_in_create_inactive_user(self):
        request = test.RequestFactory().get("/")
        form = self.sut(data=self.form_data)
        form.is_valid()
        form.create_inactive_user(request, send_email=False)

        self.assertEqual(0, len(mail.outbox))

    def test_sends_activation_email_in_create_inactive_user(self):
        request = test.RequestFactory().get("/")
        site = get_site(request)

        form = self.sut(data=self.form_data)
        form.is_valid()
        form.create_inactive_user(request, send_email=True)

        self.assertEqual(1, len(mail.outbox))
        self.assertEqual([self.form_data['email']], mail.outbox[0].to)
        self.assertEqual(settings.DEFAULT_FROM_EMAIL,
                         mail.outbox[0].from_email)
        self.assertEqual(
            form._get_activation_subject(site), mail.outbox[0].subject)

        expected_content = form._get_activation_message(
            site, form.activation_template_name)
        self.assertEqual(expected_content, mail.outbox[0].body)

        expected_html = form._get_activation_message(
            site, form.activation_html_template_name)
        self.assertHTMLEqual(expected_html, mail.outbox[0].alternatives[0][0])

    def test_send_activation_email_doesnt_use_html_when_no_html_template(
            self):
        request = test.RequestFactory().get("/")
        site = get_site(request)
        form = self.sut(data=self.form_data)
        form.is_valid()

        form.activation_html_template_name = None
        form.create_inactive_user(request, send_email=True)

        self.assertEqual(1, len(mail.outbox))
        self.assertEqual([self.form_data['email']], mail.outbox[0].to)
        self.assertEqual(settings.DEFAULT_FROM_EMAIL,
                         mail.outbox[0].from_email)
        self.assertEqual(
            form._get_activation_subject(site), mail.outbox[0].subject)

        expected_content = form._get_activation_message(
            site, form.activation_template_name)
        self.assertEqual(expected_content, mail.outbox[0].body)

        self.assertEqual([], mail.outbox[0].alternatives)

    def test_get_email_context(self):
        request = test.RequestFactory().get("/")
        site = get_site(request)
        form = self.sut(data=self.form_data)
        form.is_valid()

        form.activation_html_template_name = None
        form.create_inactive_user(request, send_email=True)

        activation_key = form.user.registrationprofile.activation_key
        activation_path = reverse(
            "registration_activate", kwargs={"activation_key": activation_key})
        activation_url = "{protocol}://{host}{path}".format(
            protocol="http", host=request.get_host(), path=activation_path)
        expected_context = dict({
            "activation_key":
            activation_key,
            "activation_url":
            activation_url,
            "expiration_days":
            settings.ACCOUNT_ACTIVATION_DAYS,
            "site":
            site,
        }, **self.form_data)
        self.assertEqual(expected_context, form.get_email_context(site))

    def test_get_email_context_when_request_is_secure(self):
        request = test.RequestFactory().get("/", secure=True)
        site = get_site(request)
        form = self.sut(data=self.form_data)
        form.is_valid()

        form.activation_html_template_name = None
        form.create_inactive_user(request, send_email=True)

        activation_key = form.user.registrationprofile.activation_key
        activation_path = reverse(
            "registration_activate", kwargs={"activation_key": activation_key})
        activation_url = "{protocol}://{host}{path}".format(
            protocol="https", host=request.get_host(), path=activation_path)
        expected_context = dict({
            "activation_key":
            activation_key,
            "activation_url":
            activation_url,
            "expiration_days":
            settings.ACCOUNT_ACTIVATION_DAYS,
            "site":
            site,
        }, **self.form_data)
        self.assertEqual(expected_context, form.get_email_context(site))
