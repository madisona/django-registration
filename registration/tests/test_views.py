from django import test
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse

from registration import forms
from registration.models import RegistrationProfile


class RegisterTests(test.TestCase):
    def test_accesses_page_successfully(self):
        response = self.client.get(reverse("registration_register"))
        self.assertEqual(200, response.status_code)

    def test_renders_to_correct_template(self):
        response = self.client.get(reverse("registration_register"))
        self.assertTemplateUsed(response, "registration/register.html")

    def test_sends_registration_form_to_template(self):
        response = self.client.get(reverse("registration_register"))
        self.failUnless(
            isinstance(response.context['form'], forms.RegistrationForm))

    def test_redirects_to_complete_page_on_success(self):
        response = self.client.post(
            reverse("registration_register"), {
                'username': 'alice',
                'email': 'alice@example.com',
                'password1': 'secret',
                'password2': 'secret',
            })
        self.assertRedirects(response, reverse("registration_complete"))

    def test_creates_inactive_user_and_profile_on_success(self):
        data = {
            'username': 'alice',
            'email': 'alice@example.com',
            'password1': 'secret',
            'password2': 'secret',
        }
        self.client.post(reverse("registration_register"), data)

        UserModel = get_user_model()
        user = UserModel.objects.get(
            **{UserModel.USERNAME_FIELD: data['username']})
        self.assertEqual(data['username'], user.username)
        self.assertEqual(data['email'], user.email)
        self.assertEqual(False, user.is_active)
        self.assertEqual(True, user.check_password(data['password1']))
        self.assertIsNotNone(user.registrationprofile.activation_key)


class RegistrationCompleteTests(test.TestCase):
    def test_accesses_page_successfully(self):
        response = self.client.get(reverse("registration_complete"))
        self.assertEqual(200, response.status_code)

    def test_renders_to_correct_template(self):
        response = self.client.get(reverse("registration_complete"))
        self.assertTemplateUsed(response,
                                "registration/registration_complete.html")


class ActivateTests(test.TestCase):
    def test_accesses_page_successfully(self):
        response = self.client.get(
            reverse("registration_activate", kwargs={'activation_key': '123'}))
        self.assertEqual(200, response.status_code)

    def test_shows_activation_failed_template_when_key_not_valid(self):
        response = self.client.get(
            reverse("registration_activate", kwargs={'activation_key': '123'}))
        self.assertTemplateUsed(response,
                                "registration/activation_failed.html")

    def test_activates_user_when_key_is_valid(
            self):
        user = RegistrationProfile.objects.create_inactive_user(
            "user", "pswd", "user@me.com")

        self.assertEqual(False, user.is_active)
        activation_key = user.registrationprofile.activation_key
        response = self.client.get(
            reverse(
                "registration_activate",
                kwargs={'activation_key': activation_key}))
        self.assertRedirects(response,
                             reverse("registration_activation_complete"))

        updated_user = get_user_model().objects.get(pk=user.pk)
        self.assertEqual(True, updated_user.is_active)
        self.assertEqual(RegistrationProfile.ACTIVATED,
                         updated_user.registrationprofile.activation_key)
