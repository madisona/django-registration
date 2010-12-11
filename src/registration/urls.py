
from django.conf.urls.defaults import patterns, url

from registration import views
urlpatterns = patterns('',
    url(r'^register/$', views.Register.as_view(), name='register'),
    url(r'^register/complete/$', views.RegistrationComplete.as_view(), name='registration_complete'),
    url(r'^activate/complete/$', views.ActivationComplete.as_view(), name='activation_complete'),
    url(r'^activate/(?P<activation_key>\w+)/$', views.Activate.as_view(), name='activate'),
    
)