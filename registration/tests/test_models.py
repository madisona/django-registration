import datetime

from django import test
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone

from registration.models import RegistrationProfile


class RegistrationManagerTests(test.TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            "aaron", "secret", "aaron@example.com")

    def test_creates_profile(self):
        RegistrationProfile.objects._create_profile(self.user)
        self.assertEqual(1, RegistrationProfile.objects.all().count())

    def test_gets_new_inactive_user(self):
        user = RegistrationProfile.objects._get_new_inactive_user(
            "adam", "secret", "adam@example.com")
        self.assertFalse(user.is_active)

    def test_creates_user_and_profile(self):
        user = RegistrationProfile.objects.create_inactive_user(
            "adam", "secret", "adam@example.com")

        self.assertEqual("adam", user.username)
        self.assertEqual("adam@example.com", user.email)
        self.assertEqual(True, user.check_password("secret"))
        self.assertIsNotNone(user.registrationprofile.activation_key)

    def test_allows_other_user_attributes_at_initial_creation(self):
        user = RegistrationProfile.objects.create_inactive_user(
            "adam",
            "secret",
            "adam@example.com",
            first_name="Adam",
            last_name="Sample")

        self.assertEqual("Adam", user.first_name)
        self.assertEqual("Sample", user.last_name)
        self.assertIsNotNone(user.registrationprofile.activation_key)

    def test_returns_false_when_activation_key_isnt_found(self):
        user = RegistrationProfile.objects.activate_user("key")
        self.assertEqual(user, False)

    def test_returns_false_if_activation_key_is_expired(self):
        user = RegistrationProfile.objects.create_inactive_user(
            "adam", "secret", "adam@example.com")

        with self.settings(ACCOUNT_ACTIVATION_DAYS=0):
            activation_key = user.registrationprofile.activation_key
            activated_user = RegistrationProfile.objects.activate_user(
                activation_key)
        self.assertEqual(activated_user, False)

    def test_activates_user(self):
        user = RegistrationProfile.objects.create_inactive_user(
            "adam", "secret", "adam@example.com")

        activated_user = RegistrationProfile.objects.activate_user(
            user.registrationprofile.activation_key)

        updated_user = get_user_model().objects.get(pk=user.pk)
        self.assertEqual(updated_user, activated_user)
        self.assertEqual(True, updated_user.is_active)
        self.assertEqual(RegistrationProfile.ACTIVATED,
                         updated_user.registrationprofile.activation_key)

    @test.override_settings(ACCOUNT_ACTIVATION_DAYS=1)
    def test_deletes_expired_profiles_profiles(self):
        # Active user, not activated profile (not expired)
        user_one = get_user_model().objects.create_user("one")
        p1 = RegistrationProfile.objects.create(
            user=user_one, activation_key="some-key")

        # inactive user, expired profile
        user_two = get_user_model().objects.create(
            username="two",
            date_joined=timezone.now() - datetime.timedelta(days=2),
            is_active=False)
        RegistrationProfile.objects.create(
            user=user_two, activation_key="some-key")

        # active user, activated profile
        user_three = get_user_model().objects.create(
            username="three",
            date_joined=timezone.now() - datetime.timedelta(days=10))
        p3 = RegistrationProfile.objects.create(
            user=user_three,
            activation_key=RegistrationProfile.ACTIVATED)

        # inactive user, profile not yet expired
        user_four = get_user_model().objects.create(
            username="four", is_active=False)
        p4 = RegistrationProfile.objects.create(
            user=user_four, activation_key="some-key")

        # inactive user, profile already registered
        user_five = get_user_model().objects.create(
            username="five", is_active=False)
        p5 = RegistrationProfile.objects.create(
            user=user_five,
            activation_key=RegistrationProfile.ACTIVATED)

        # Active user, not activated profile (already expired)
        user_six = get_user_model().objects.create(
            username="six",
            date_joined=timezone.now() - datetime.timedelta(days=2))
        p6 = RegistrationProfile.objects.create(
            user=user_six, activation_key="some-key")

        # expect to delete user two.
        RegistrationProfile.objects.delete_expired_users()

        remaining_profiles = RegistrationProfile.objects.all().order_by(
            "user__pk")
        self.assertQuerysetEqual(remaining_profiles,
                                 [repr(p) for p in [p1, p3, p4, p5, p6]])


class RegistrationProfileModelTests(test.TestCase):
    def setUp(self):
        self.sample_user = RegistrationProfile.objects.create_inactive_user(
            "alice",
            "secret",
            "alice@example.com", )
        self.expired_user = RegistrationProfile.objects.create_inactive_user(
            "bob",
            "secret",
            "bob@example.com", )
        self.expired_user.date_joined -= datetime.timedelta(
            days=settings.ACCOUNT_ACTIVATION_DAYS + 1)
        self.expired_user.save()

    def test_uses_user_in_string_representation(self):
        user = get_user_model().objects.create_user("aaron", "secret",
                                                    "aaron@example.com")
        profile = RegistrationProfile(user=user)
        self.assertTrue(str(user) in str(profile))

    def test_is_not_expired_if_expiration_date_has_not_passed(self):
        profile = RegistrationProfile.objects.get(user=self.sample_user)
        self.assertFalse(profile.activation_key_expired())

    def test_is_expired_if_expiration_date_has_passed(self):
        profile = RegistrationProfile.objects.get(
            user=self.expired_user)
        self.assertTrue(profile.activation_key_expired())

    def test_is_expired_if_already_activated(self):
        profile = RegistrationProfile.objects.get(user=self.sample_user)
        profile.activation_key = RegistrationProfile.ACTIVATED
        self.assertTrue(profile.activation_key_expired())
