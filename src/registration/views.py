# Create your views here.

from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from django.core.urlresolvers import reverse

from registration import forms

class Register(FormView):
    template_name = 'registration/register.html'
    form_class = forms.RegistrationForm
    
    def get_success_url(self):
        return reverse("registration:registration_complete")

class RegistrationComplete(TemplateView):
    template_name = 'registration/registration_complete.html'