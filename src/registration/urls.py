
from django.conf.urls.defaults import patterns, url

from registration import views
urlpatterns = patterns('',
    url(r'^register/$', views.Register.as_view(), name='register'),
    url(r'^register/complete/$', views.RegistrationComplete.as_view(), name='registration_complete'),


)