from django.conf.urls import url

from registration import views
from registration import auth_urls

registration_urls = [
    url(
        r'^register/$', views.Register.as_view(),
        name='registration_register'),
    url(
        r'^register/complete/$',
        views.RegistrationComplete.as_view(),
        name='registration_complete'),
    url(
        r'^activate/complete/$',
        views.ActivationComplete.as_view(),
        name='registration_activation_complete'),
    url(
        r'^activate/(?P<activation_key>\w+)/$',
        views.Activate.as_view(),
        name='registration_activate'),
]

urlpatterns = registration_urls + auth_urls.urlpatterns
