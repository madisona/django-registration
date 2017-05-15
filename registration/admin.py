from django.contrib import admin

from registration import models
from registration import get_site


class RegistrationAdmin(admin.ModelAdmin):
    actions = ('activate_users', 'resend_activation_email')
    list_display = ('user', 'activation_key_expired')
    raw_id_fields = ('user', )
    search_fields = ('user__username', 'user__first_name')

    def activate_users(self, request, queryset):
        for profile in queryset:
            models.RegistrationProfile.objects.activate_user(
                profile.activation_key)

    def resend_activation_email(self, request, queryset):
        site = get_site(request)
        for profile in queryset:
            if not profile.activation_key_expired():
                profile.send_activation_email(site)


admin.site.register(models.RegistrationProfile, RegistrationAdmin)
