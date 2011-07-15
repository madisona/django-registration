
from mock import patch, Mock

from django import test
from django.core.urlresolvers import reverse

from registration import forms

class RegisterTests(test.TestCase):

    def test_accesses_page_successfully(self):
        response = self.client.get(reverse("registration_register"))
        self.assertEqual(200, response.status_code)

    def test_renders_to_correct_template(self):
        response = self.client.get(reverse("registration_register"))
        self.assertTemplateUsed(response, "registration/register.html")

    def test_sends_registration_form_to_template(self):
        response = self.client.get(reverse("registration_register"))
        self.failUnless(isinstance(response.context['form'], forms.RegistrationForm))

    def test_redirects_to_complete_page_on_success(self):
        response = self.client.post(reverse("registration_register"), {
            'username': 'alice',
            'email': 'alice@example.com',
            'password1': 'secret',
            'password2': 'secret',
        })
        self.assertRedirects(response, reverse("registration_complete"))

    @patch("registration.views.get_site")
    @patch("registration.models.RegistrationProfile.objects")
    def test_creates_inactive_user_on_success(self, manager, get_site):
        data = {
            'username': 'alice',
            'email': 'alice@example.com',
            'password1': 'secret',
            'password2': 'secret',
        }
        self.client.post(reverse("registration_register"), data)
        self.assertEqual(((data['username'], data['password1'], data['email'], get_site.return_value), {}),
                         manager.create_inactive_user.call_args)

class RegistrationCompleteTests(test.TestCase):

    def test_accesses_page_successfully(self):
        response = self.client.get(reverse("registration_complete"))
        self.assertEqual(200, response.status_code)

    def test_renders_to_correct_template(self):
        response = self.client.get(reverse("registration_complete"))
        self.assertTemplateUsed(response, "registration/registration_complete.html")

class ActivateTests(test.TestCase):

    def test_accesses_page_successfully(self):
        response = self.client.get(reverse("registration_activate", kwargs={'activation_key': '123'}))
        self.assertEqual(200, response.status_code)

    def test_shows_activation_failed_template_when_key_not_valid(self):
        response = self.client.get(reverse("registration_activate", kwargs={'activation_key': '123'}))
        self.assertTemplateUsed(response, "registration/activation_failed.html")

    @patch('registration.models.RegistrationProfile.objects.activate_user', Mock(return_value=True))
    def test_redirects_to_complete_page_when_key_is_valid(self):
        response = self.client.get(reverse("registration_activate", kwargs={'activation_key': '123'}))
        self.assertRedirects(response, reverse("registration_activation_complete"))