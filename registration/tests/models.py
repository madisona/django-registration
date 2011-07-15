
import datetime
from mock import patch, Mock

from django import test
from django.conf import settings
from django.contrib.auth.models import User

from registration import models

class RegistrationManagerTests(test.TestCase):

    def setUp(self):
        self.user = User.objects.create_user("aaron", "secret", "aaron@example.com")

    def test_creates_profile(self):
        models.RegistrationProfile.objects._create_profile(self.user)
        self.assertEqual(1, models.RegistrationProfile.objects.all().count())

    def test_gets_new_inactive_user(self):
        user = models.RegistrationProfile.objects._get_new_inactive_user("adam", "secret", "adam@example.com")
        self.assertFalse(user.is_active)

    @patch("registration.models.RegistrationProfile.objects._get_new_inactive_user")
    @patch("registration.models.RegistrationProfile.objects._create_profile")
    def test_creates_user_and_profile(self, create_profile, get_new_inactive_user):
        user = models.RegistrationProfile.objects.create_inactive_user("adam", "secret", "adam@example.com", Mock())

        self.assertTrue(get_new_inactive_user.called)
        self.assertEqual(user, get_new_inactive_user.return_value)
        self.assertEqual([(user,), {}], create_profile.call_args)

    @patch("registration.models.RegistrationProfile.objects._create_profile")
    def test_sends_email_if_requested_in_create_inactive_user(self, create_profile):
        models.RegistrationProfile.objects.create_inactive_user(
                "adam", "secret", "adam@example.com", Mock(), send_email=True)

        self.assertTrue(create_profile.return_value.send_activation_email.called)

    def test_returns_false_if_activation_key_isnt_found(self):
        user = models.RegistrationProfile.objects.activate_user("key")
        self.assertEqual(user, False)

    @patch("registration.models.RegistrationProfile.objects.get")
    def test_returns_false_if_activation_key_is_expired(self, get_mock):
        get_mock.return_value.activation_key_expired.return_value = True

        user = models.RegistrationProfile.objects.activate_user(Mock())
        self.assertEqual(user, False)

    def test_sets_active_status_and_saves(self):
        user = Mock()
        active_user = models.RegistrationProfile.objects._do_activate_user(user)

        self.assertEqual(active_user.is_active, True)
        self.assertTrue(user.save.called, "didnt save user")

    def test_sets_activation_key_and_saves(self):
        profile = Mock()
        models.RegistrationProfile.objects._do_activate_profile(profile)

        self.assertEqual(models.RegistrationProfile.ACTIVATED, profile.activation_key)
        self.assertTrue(profile.save.called, "didnt save profile")

    @patch("registration.models.RegistrationProfile.objects._do_activate_user")
    @patch("registration.models.RegistrationProfile.objects._do_activate_profile")
    @patch("registration.models.RegistrationProfile.objects.get")
    def test_activates_and_returns_user(self, get_mock, do_activate_profile, do_activate_user):
        profile = get_mock.return_value
        profile.activation_key_expired.return_value = False

        active_user = models.RegistrationProfile.objects.activate_user(Mock())
        self.assertEqual([(profile.user,), {}], do_activate_user.call_args)
        self.assertEqual([(profile,), {}], do_activate_profile.call_args)
        self.assertEqual(do_activate_user.return_value, active_user)

    @patch("registration.models.RegistrationProfile.objects.all")
    def test_deletes_expired_user_if_activation_key_is_expired_and_user_is_not_active(self, all_mock):
        user = Mock()
        user.is_active = False

        profile = Mock()
        profile.user = user
        profile.activation_key_expired.return_value = True

        all_mock.return_value = [profile]
        models.RegistrationProfile.objects.delete_expired_users()
        self.assertTrue(user.delete.called)

    @patch("registration.models.RegistrationProfile.objects.all")
    def test_does_not_delete_user_if_activation_key_has_not_expired(self, all_mock):
        user = Mock()
        user.is_active = False

        profile = Mock()
        profile.user = user
        profile.activation_key_expired.return_value = False

        all_mock.return_value = [profile]
        models.RegistrationProfile.objects.delete_expired_users()
        self.assertFalse(user.delete.called)

    @patch("registration.models.RegistrationProfile.objects.all")
    def test_does_not_delete_user_if_user_is_active(self, all_mock):
        user = Mock()
        user.is_active = True

        profile = Mock()
        profile.user = user
        profile.activation_key_expired.return_value = True

        all_mock.return_value = [profile]
        models.RegistrationProfile.objects.delete_expired_users()
        self.assertFalse(user.delete.called)

class RegistrationProfileModelTests(test.TestCase):

    def setUp(self):
        self.sample_user = models.RegistrationProfile.objects.create_inactive_user(
            "alice",
            "secret",
            "alice@example.com", Mock(),
        )
        self.expired_user = models.RegistrationProfile.objects.create_inactive_user(
            "bob",
            "secret",
            "bob@example.com", Mock(),
        )
        self.expired_user.date_joined -= datetime.timedelta(days=settings.ACCOUNT_ACTIVATION_DAYS + 1)
        self.expired_user.save()

    def test_uses_user_in_string_representation(self):
        user = User.objects.create_user("aaron", "secret", "aaron@example.com")
        profile = models.RegistrationProfile(user=user)
        self.assertTrue(str(user) in str(profile))

    def test_is_not_expired_if_expiration_date_has_not_passed(self):
        profile = models.RegistrationProfile.objects.get(user=self.sample_user)
        self.assertFalse(profile.activation_key_expired())

    def test_is_expired_if_expiration_date_has_passed(self):
        profile = models.RegistrationProfile.objects.get(user=self.expired_user)
        self.assertTrue(profile.activation_key_expired())

    def test_is_expired_if_already_activated(self):
        profile = models.RegistrationProfile.objects.get(user=self.sample_user)
        profile.activation_key = models.RegistrationProfile.ACTIVATED
        self.assertTrue(profile.activation_key_expired())

    @patch("registration.models.RegistrationProfile._get_activation_message")
    @patch("registration.models.RegistrationProfile._get_activation_subject")
    def test_gets_current_site_and_sends_to_get_templates(self, get_subject, get_message):
        registration_profile = models.RegistrationProfile(user=self.sample_user)
        current_site = Mock()
        registration_profile.send_activation_email(current_site)
        self.assertEqual([(current_site,), {}], get_subject.call_args)
        self.assertEqual([(current_site,), {}], get_message.call_args)

    @patch('registration.models.User.email_user', Mock())
    @patch("registration.models.RegistrationProfile._get_activation_message")
    @patch("registration.models.RegistrationProfile._get_activation_subject")
    @patch("registration.models.settings")
    def test_sends_proper_arguments_to_send_mail_command(self, settings_mock, get_subject, get_message):
        registration_profile = models.RegistrationProfile(user=self.sample_user)
        registration_profile.send_activation_email(Mock())
        self.assertEqual([(
            get_subject.return_value,
            get_message.return_value,
            settings_mock.DEFAULT_FROM_EMAIL,
        ), {}], registration_profile.user.email_user.call_args)

    @patch("registration.models.render_to_string")
    def test_renders_email_subject_to_string(self, render_to_string):
        render_to_string.return_value = "Activation email"
        site_mock = Mock()
        subject = models.RegistrationProfile()._get_activation_subject(site_mock)

        self.assertEqual([(
            models.RegistrationProfile.activation_subject_template_name,
            {'site': site_mock},
        ), {}], render_to_string.call_args)
        self.assertEqual(render_to_string.return_value, subject)

    @patch("registration.models.render_to_string")
    def test_forces_email_subject_to_be_one_line(self, render_to_string):
        render_to_string.return_value = "Activation \nemail"
        subject = models.RegistrationProfile()._get_activation_subject(Mock)
        self.assertEqual("Activation email", subject)

    @patch("registration.models.settings")
    @patch("registration.models.render_to_string")
    def test_renders_email_message_to_string(self, render_to_string, settings_mock):
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