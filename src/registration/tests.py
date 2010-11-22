
import datetime
from mock import patch, Mock

from django import test
from django.conf import settings
from django.contrib.auth.models import User

from registration import models

#class RegistrationTestCase(test.TestCase):
#
#    def setUp(self):
#        self.sample_user = models.RegistrationProfile.objects.create_inactive_user(
#            username="alice",
#            password="secret",
#            email="alice@example.com"
#        )
#        self.expired_user = models.RegistrationProfile.objects.create_inactive_user(
#            username="bob",
#            password="secret",
#            email="bob@example.com"
#        )
#        self.expired_user.date_joined -= datetime.timedelta(days=settings.ACCOUNT_ACTIVATION_DAYS + 1)
#        self.expired_user.save()
#
#class RegistrationProfileModelTests(RegistrationTestCase):
#
#    def should_use_user_in_string_representation(self):
#        profile = models.RegistrationProfile.objects.create(user=self.sample_user)
#        self.assertTrue(str(self.sample_user) in str(profile))

class RegistrationManagerTests(test.TestCase):

    def setUp(self):
        self.user = User.objects.create_user("aaron", "secret", "aaron@example.com")

    def should_create_profile(self):
        profile = models.RegistrationProfile.objects._create_profile(self.user)

        self.assertEqual(1, models.RegistrationProfile.objects.all().count())
        self.assertTrue(models.SHA1_RE.search(profile.activation_key))

    def should_get_new_inactive_user(self):
        user = models.RegistrationProfile.objects._get_new_inactive_user("adam", "secret", "adam@example.com")
        self.assertFalse(user.is_active)

    @patch("registration.models.RegistrationProfile.objects._get_new_inactive_user")
    @patch("registration.models.RegistrationProfile.objects._create_profile")
    def should_create_user_and_profile(self, create_profile, get_new_inactive_user):
        user = models.RegistrationProfile.objects.create_inactive_user("adam", "secret", "adam@example.com")

        self.assertTrue(get_new_inactive_user.called)
        self.assertEqual(user, get_new_inactive_user.return_value)
        self.assertEqual([(user,), {}], create_profile.call_args)

    def should_call_profile_callback_with_user_if_it_is_given(self):
        profile_callback = Mock()
        user = models.RegistrationProfile.objects.create_inactive_user(
                "adam", "secret", "adam@example.com", profile_callback = profile_callback)

        self.assertEqual([(user,), {}], profile_callback.call_args)

    @patch("registration.models.RegistrationProfile.objects._create_profile")
    @patch("registration.models.RegistrationProfile.objects._send_activation_email")
    def should_send_email_if_requested_in_create_inactive_user(self, send_email, create_profile):
        user = models.RegistrationProfile.objects.create_inactive_user(
                "adam", "secret", "adam@example.com", send_email=True)

        self.assertEqual([(user, create_profile.return_value), {}], send_email.call_args)

    @patch("registration.models.render_to_string")
    def should_render_email_subject_to_string(self, render_to_string):
        render_to_string.return_value = "Activation email"
        site_mock = Mock()
        subject = models.RegistrationProfile.objects._get_activation_subject(site_mock)
        
        self.assertEqual([(
            models.RegistrationProfile.objects.activation_subject_template_name,
            {'site': site_mock},
        ), {}], render_to_string.call_args)
        self.assertEqual(render_to_string.return_value, subject)

    @patch("registration.models.render_to_string")
    def should_force_email_subject_to_be_one_line(self, render_to_string):
        render_to_string.return_value = "Activation \nemail"
        subject = models.RegistrationProfile.objects._get_activation_subject(Mock)
        self.assertEqual("Activation email", subject)

    @patch("registration.models.settings")
    @patch("registration.models.render_to_string")
    def should_render_email_message_to_string(self, render_to_string, settings_mock):
        activation_key = Mock()
        current_site = Mock()
        message = models.RegistrationProfile.objects._get_activation_message(activation_key, current_site)

        self.assertEqual([(
            models.RegistrationProfile.objects.activation_template_name, {
                'site': current_site,
                'activation_key': activation_key,
                'expiration_days': settings_mock.ACCOUNT_ACTIVATION_DAYS,
             },
        ), {}], render_to_string.call_args)
        self.assertEqual(render_to_string.return_value, message)

    @patch("registration.models.RegistrationProfile.objects._get_activation_message")
    @patch("registration.models.RegistrationProfile.objects._get_activation_subject")
    @patch('django.contrib.sites.models.Site.objects.get_current')
    def should_get_current_site_and_send_to_get_templates(self, get_current, get_subject, get_message):
        user = Mock()
        registration_profile = Mock()
        models.RegistrationProfile.objects._send_activation_email(user, registration_profile)
        self.assertEqual([(get_current.return_value,), {}], get_subject.call_args)
        self.assertEqual([(registration_profile.activation_key, get_current.return_value), {}],
                         get_message.call_args)

    @patch("registration.models.RegistrationProfile.objects._get_activation_message")
    @patch("registration.models.RegistrationProfile.objects._get_activation_subject")
    @patch("registration.models.settings")
    @patch('registration.models.send_mail')
    def should_send_proper_arguments_to_send_mail_command(self, send_mail, settings_mock, get_subject, get_message):
        user = Mock()
        models.RegistrationProfile.objects._send_activation_email(user, Mock())
        self.assertEqual([(), {
            "from_email": settings_mock.DEFAULT_FROM_EMAIL,
            "recipient_list": [user.email],
            "subject": get_subject.return_value,
            "message": get_message.return_value,
        }], send_mail.call_args)

        


