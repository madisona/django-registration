
from django.contrib import admin
from django.contrib.sites.models import RequestSite
from django.contrib.sites.models import Site

from registration import models

class RegistrationAdmin(admin.ModelAdmin):
    actions = ('activate_users', 'resend_activation_email')
    list_display = ('user', 'activation_key_expired')
    raw_id_fields = ('user',)
    search_fields = ('user__username', 'user__first_name')

    def activate_users(self, request, queryset):
        'activates selected users'
        for profile in queryset:
            models.RegistrationProfile.objects.activate_user(profile.activation_key)

    def _get_site(self, request):
        if Site._meta.installed:
            site = Site.objects.get_current()
        else:
            site = RequestSite(request)

    def resend_activation_email(self, request, queryset):
        'resends activation email for selected users'
        site = self._get_site(request)
        for profile in queryset:
            if not profile.activation_key_expired():
                profile.send_activation_email(site)

admin.site.register(models.RegistrationProfile, RegistrationAdmin)