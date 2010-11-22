
import datetime
import random
import re
from hashlib import sha1


from django.db import models
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.contrib.sites.models import Site

SHA1_RE = re.compile('^[a-f0-9]{40}$')

class RegistrationManager(models.Manager):
    "Provides shortcuts to account creation and activation"

    activation_subject_template_name = "registration/activation_email_subject.txt"
    activation_template_name = "registration/activation_email.txt"

#    def activate_user(self, activation_key):
#        "returns user object if successful, otherwise returns false"
#        if SHA1_RE.search(activation_key):
#            try:
#                profile = self.get(activation_key=activation_key)
#            except self.model.DoesNotExist:
#                return False
#
#            if not profile.activation_key_expired():
#                user = profile.user
#                user.is_active = True
#                user.save()
#                profile.activation_key = self.model.ACTIVATED
#                profile.save()
#                return user
#        return False
#
    def create_inactive_user(self, username, password, email, send_email=True, profile_callback=None):
        new_user = self._get_new_inactive_user(username, password, email)
        registration_profile = self._create_profile(new_user)
        
        if profile_callback is not None:
            profile_callback(new_user)

        if send_email:
            self._send_activation_email(new_user, registration_profile)
        return new_user

    def _get_new_inactive_user(self, username, password, email):
        new_user = User.objects.create_user(username, email, password)
        new_user.is_active = False
        new_user.save()
        return new_user

    def _create_profile(self, user):
        salt = sha1(str(random.random())).hexdigest()[:5]
        activation_key = sha1(salt + user.username).hexdigest()
        return self.create(user=user, activation_key=activation_key)

    def _get_activation_subject(self, site):
        subject = render_to_string(self.activation_subject_template_name, {'site': site})
        return ''.join(subject.splitlines())

    def _get_activation_message(self, activation_key, site):
        return render_to_string(self.activation_template_name, {
            'site': site,
            'activation_key': activation_key,
            'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS,
        })

    def _send_activation_email(self, user, registration_profile):
        current_site = Site.objects.get_current()
        send_mail(
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            subject=self._get_activation_subject(current_site),
            message=self._get_activation_message(registration_profile.activation_key, current_site),
        )


class RegistrationProfile(models.Model):
    ACTIVATED = u"ALREADY_ACTIVATED"

    user = models.ForeignKey(User, unique=True)
    activation_key = models.CharField(max_length=40)

    objects = RegistrationManager()

    def __unicode__(self):
        return u"Registration information for %s" % self.user

