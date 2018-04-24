import datetime
import six
import random
from hashlib import sha1

from django.db import models
from django.db import transaction
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.timezone import now as utc_now


class RegistrationManager(models.Manager):
    """Provides shortcuts to account creation and activation"""

    @transaction.atomic
    def create_inactive_user(self, username, password, email, **kwargs):
        new_user = self._get_new_inactive_user(username, password, email,
                                               **kwargs)
        self._create_profile(new_user)
        return new_user

    def activate_user(self, activation_key):
        """
        returns user object if successful, otherwise returns false
        """
        try:
            profile = self.get(activation_key=activation_key)
        except self.model.DoesNotExist:
            return False
        if not profile.activation_key_expired():
            active_user = self._do_activate_user(profile.user)
            self._do_activate_profile(profile)
            return active_user
        return False

    def delete_expired_users(self):
        """
        Deletes inactive users with expired profiles.
        """
        for profile in self.filter(user__is_active=False).exclude(
                activation_key=RegistrationProfile.ACTIVATED):
            if profile.activation_key_expired():
                profile.user.delete()

    def _do_activate_user(self, user):
        user.is_active = True
        user.save()
        return user

    def _do_activate_profile(self, profile):
        profile.activation_key = self.model.ACTIVATED
        profile.save()

    def _get_new_inactive_user(self, username, password, email, **kwargs):
        new_user = get_user_model().objects.create_user(
            username, email, password, **kwargs)
        new_user.is_active = False
        new_user.save()
        return new_user

    def _create_profile(self, user):
        salt = sha1(six.text_type(
            random.random()).encode("utf-8")).hexdigest()[:5]
        activation_key = sha1(
            six.text_type(salt + user.username).encode('utf-8')).hexdigest()
        return self.create(user=user, activation_key=activation_key)


class RegistrationProfile(models.Model):
    ACTIVATED = u"ALREADY_ACTIVATED"

    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    activation_key = models.CharField(max_length=40)

    objects = RegistrationManager()

    def __str__(self):
        return u"Registration information for %s" % self.user

    def activation_key_expired(self):
        expiration_date = datetime.timedelta(
            days=settings.ACCOUNT_ACTIVATION_DAYS)
        return (self.activation_key == self.ACTIVATED) or \
               (self.user.date_joined + expiration_date <= utc_now())
