
from django import test
from django.contrib.auth import get_user_model

from registration import forms


class RegistrationFormTests(test.TestCase):

    def test_requires_username_to_be_unique(self):
        get_user_model().objects.create_user("alice", "alice@example.com", "secret")
        registration_form = forms.RegistrationForm({
            "username": "alice",
            "email": "alice@example.com",
            "password1": "secret",
            "password2": "secret",
        })
        self.failIf(registration_form.is_valid())
        self.assertEqual(["Username 'alice' is not available."],
                         registration_form.errors['username'])

    def test_requires_passwords_to_match(self):
        registration_form = forms.RegistrationForm({
            "username": "alice",
            "email": "alice@example.com",
            "password1": "secret",
            "password2": "pswd",
        })
        self.failIf(registration_form.is_valid())
        self.assertEqual(["Passwords must match."],
                         registration_form.errors['__all__'])
