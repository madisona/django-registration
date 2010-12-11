
from django import test
from django.core.urlresolvers import reverse

from registration import forms

class RegisterTests(test.TestCase):

    def should_access_page_successfully(self):
        response = self.client.get(reverse("registration:register"))
        self.assertEqual(200, response.status_code)

    def should_send_registration_form_to_template(self):
        response = self.client.get(reverse("registration:register"))
        self.failUnless(isinstance(response.context['form'], forms.RegistrationForm))

    def should_redirect_to_complete_page_on_success(self):
        response = self.client.post(reverse("registration:register"), {
            'username': 'alice',
            'email': 'alice@example.com',
            'password1': 'secret',
            'password2': 'secret',
        })
        self.assertRedirects(response, reverse("registration:registration_complete"))

class RegistrationCompleteTests(test.TestCase):

    def should_access_page_successfully(self):
        response = self.client.get(reverse("registration:registration_complete"))
        self.assertEqual(200, response.status_code)

    def should_render_to_correct_template(self):
        response = self.client.get(reverse("registration:registration_complete"))
        self.assertTemplateUsed(response, "registration/registration_complete.html")