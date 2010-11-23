
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


class RegistrationManagerTests(test.TestCase):

    def setUp(self):
        self.user = User.objects.create_user("aaron", "secret", "aaron@example.com")

    def should_create_profile(self):
        profile = models.RegistrationProfile.objects._create_profile(self.user)
        self.assertEqual(1, models.RegistrationProfile.objects.all().count())

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
    def should_send_email_if_requested_in_create_inactive_user(self, create_profile):
        user = models.RegistrationProfile.objects.create_inactive_user(
                "adam", "secret", "adam@example.com", send_email=True)

        self.assertTrue(create_profile.return_value.send_activation_email.called)

    def should_return_false_if_activation_key_isnt_found(self):
        user = models.RegistrationProfile.objects.activate_user("key")
        self.assertEqual(user, False)

    @patch("registration.models.RegistrationProfile.objects.get")
    def should_return_false_if_activation_key_is_expired(self, get_mock):
        get_mock.return_value.activation_key_expired.return_value = True

        user = models.RegistrationProfile.objects.activate_user(Mock())
        self.assertEqual(user, False)

    def should_set_active_status_and_save(self):
        user = Mock()
        active_user = models.RegistrationProfile.objects._do_activate_user(user)

        self.assertEqual(active_user.is_active, True)
        self.assertTrue(user.save.called, "didnt save user")

    def should_set_activation_key_and_save(self):
        profile = Mock()
        models.RegistrationProfile.objects._do_activate_profile(profile)

        self.assertEqual(models.RegistrationProfile.ACTIVATED, profile.activation_key)
        self.assertTrue(profile.save.called, "didnt save profile")

    @patch("registration.models.RegistrationProfile.objects._do_activate_user")
    @patch("registration.models.RegistrationProfile.objects._do_activate_profile")
    @patch("registration.models.RegistrationProfile.objects.get")
    def should_activate_and_return_user(self, get_mock, do_activate_profile, do_activate_user):
        profile = get_mock.return_value
        profile.activation_key_expired.return_value = False

        active_user = models.RegistrationProfile.objects.activate_user(Mock())
        self.assertEqual([(profile.user,), {}], do_activate_user.call_args)
        self.assertEqual([(profile,), {}], do_activate_profile.call_args)
        self.assertEqual(do_activate_user.return_value, active_user)

class RegistrationProfileModelTests(test.TestCase):

    def setUp(self):
        self.sample_user = models.RegistrationProfile.objects.create_inactive_user(
            username="alice",
            password="secret",
            email="alice@example.com"
        )
        self.expired_user = models.RegistrationProfile.objects.create_inactive_user(
            username="bob",
            password="secret",
            email="bob@example.com"
        )
        self.expired_user.date_joined -= datetime.timedelta(days=settings.ACCOUNT_ACTIVATION_DAYS + 1)
        self.expired_user.save()

    def should_use_user_in_string_representation(self):
        user = User.objects.create_user("aaron", "secret", "aaron@example.com")
        profile = models.RegistrationProfile(user=user)
        self.assertTrue(str(user) in str(profile))

    def should_not_be_expired_if_expiration_date_has_not_passed(self):
        profile = models.RegistrationProfile.objects.get(user=self.sample_user)
        self.assertFalse(profile.activation_key_expired())

    def should_be_expired_if_expiration_date_has_passed(self):
        profile = models.RegistrationProfile.objects.get(user=self.expired_user)
        self.assertTrue(profile.activation_key_expired())

    def should_be_expired_if_already_activated(self):
        profile = models.RegistrationProfile.objects.get(user=self.sample_user)
        profile.activation_key = models.RegistrationProfile.ACTIVATED
        self.assertTrue(profile.activation_key_expired())

    @patch("registration.models.RegistrationProfile._get_activation_message")
    @patch("registration.models.RegistrationProfile._get_activation_subject")
    @patch('django.contrib.sites.models.Site.objects.get_current')
    def should_get_current_site_and_send_to_get_templates(self, get_current, get_subject, get_message):
        registration_profile = models.RegistrationProfile(user=self.sample_user)
        registration_profile.send_activation_email()
        self.assertEqual([(get_current.return_value,), {}], get_subject.call_args)
        self.assertEqual([(get_current.return_value,), {}], get_message.call_args)

    @patch('registration.models.User.email_user', Mock())
    @patch("registration.models.RegistrationProfile._get_activation_message")
    @patch("registration.models.RegistrationProfile._get_activation_subject")
    @patch("registration.models.settings")
    def should_send_proper_arguments_to_send_mail_command(self, settings_mock, get_subject, get_message):
        registration_profile = models.RegistrationProfile(user=self.sample_user)
        registration_profile.send_activation_email()
        self.assertEqual([(
            get_subject.return_value,
            get_message.return_value,
            settings_mock.DEFAULT_FROM_EMAIL,
        ), {}], registration_profile.user.email_user.call_args)

    @patch("registration.models.render_to_string")
    def should_render_email_subject_to_string(self, render_to_string):
        render_to_string.return_value = "Activation email"
        site_mock = Mock()
        subject = models.RegistrationProfile()._get_activation_subject(site_mock)

        self.assertEqual([(
            models.RegistrationProfile.activation_subject_template_name,
            {'site': site_mock},
        ), {}], render_to_string.call_args)
        self.assertEqual(render_to_string.return_value, subject)

    @patch("registration.models.render_to_string")
    def should_force_email_subject_to_be_one_line(self, render_to_string):
        render_to_string.return_value = "Activation \nemail"
        subject = models.RegistrationProfile()._get_activation_subject(Mock)
        self.assertEqual("Activation email", subject)

    @patch("registration.models.settings")
    @patch("registration.models.render_to_string")
    def should_render_email_message_to_string(self, render_to_string, settings_mock):
        profile = models.RegistrationProfile(activation_key=Mock())
        current_site = Mock()
        message = profile._get_activation_message(current_site)

        self.assertEqual([(
            models.RegistrationProfile.activation_template_name, {
                'site': current_site,
                'activation_key': profile.activation_key,
                'expiration_days': settings_mock.ACCOUNT_ACTIVATION_DAYS,
             },
        ), {}], render_to_string.call_args)
        self.assertEqual(render_to_string.return_value, message)