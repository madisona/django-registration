# Create your views here.

from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from django.core.urlresolvers import reverse

from registration import forms
from registration import models
from registration import get_site

class Register(FormView):
    template_name = 'registration/register.html'
    form_class = forms.RegistrationForm
    
    def get_success_url(self):
        return reverse("registration:registration_complete")

    def form_valid(self, form):
        # activate user...
        models.RegistrationProfile.objects.create_inactive_user(
            form.cleaned_data['username'],
            form.cleaned_data['password1'],
            form.cleaned_data['email'],
            get_site(self.request)
        )
        return super(Register, self).form_valid(form)

class RegistrationComplete(TemplateView):
    template_name = 'registration/registration_complete.html'