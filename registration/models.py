
import datetime
import random
from hashlib import sha1

from django.db import models
from django.db import transaction
from django.conf import settings
from django.template.loader import render_to_string
from django.contrib.auth.models import User


class RegistrationManager(models.Manager):
    """Provides shortcuts to account creation and activation"""

    @transaction.atomic
    def create_inactive_user(self, username, password, email,
                             site, send_email=True):
        new_user = self._get_new_inactive_user(username, password, email)
        registration_profile = self._create_profile(new_user)

        if send_email:
            registration_profile.send_activation_email(site)
        return new_user

    def activate_user(self, activation_key):
        """returns user object if successful, otherwise returns false"""
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
        for profile in self.all():
            if profile.activation_key_expired():
                user = profile.user
                if not user.is_active:
                    user.delete()

    def _do_activate_user(self, user):
        user.is_active = True
        user.save()
        return user

    def _do_activate_profile(self, profile):
        profile.activation_key = self.model.ACTIVATED
        profile.save()

    def _get_new_inactive_user(self, username, password, email):
        new_user = User.objects.create_user(username, email, password)
        new_user.is_active = False
        new_user.save()
        return new_user

    def _create_profile(self, user):
        salt = sha1(str(random.random())).hexdigest()[:5]
        activation_key = sha1(salt + user.username).hexdigest()
        return self.create(user=user, activation_key=activation_key)


class RegistrationProfile(models.Model):
    ACTIVATED = u"ALREADY_ACTIVATED"
    activation_subject_template_name = "registration/activation_email_subject.txt"
    activation_template_name = "registration/activation_email.txt"

    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    activation_key = models.CharField(max_length=40)

    objects = RegistrationManager()

    def __unicode__(self):
        return u"Registration information for %s" % self.user

    def activation_key_expired(self):
        expiration_date = datetime.timedelta(days=settings.ACCOUNT_ACTIVATION_DAYS)
        return self.activation_key == self.ACTIVATED or \
               (self.user.date_joined + expiration_date <= datetime.datetime.now())

    def send_activation_email(self, current_site):
        subject = self._get_activation_subject(current_site)
        message = self._get_activation_message(current_site)

        self.user.email_user(subject, message, settings.DEFAULT_FROM_EMAIL)

    def _get_activation_subject(self, site):
        subject = render_to_string(self.activation_subject_template_name, {'site': site})
        return ''.join(subject.splitlines())

    def _get_activation_message(self, site):
        return render_to_string(self.activation_template_name, {
            'site': site,
            'activation_key': self.activation_key,
            'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS,
        })
