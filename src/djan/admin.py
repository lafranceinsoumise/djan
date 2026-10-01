from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.urls import path
from djan.models import Redirection
from djan.two_factor import OptionalOTPAdminAuthenticationForm, two_factor_view


@admin.register(Redirection)
class RedirectionAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {"fields": ("site", "short_url", "destination_url", "http_status")}),
        (_("Parameters"), {"fields": ("params_mode", "unique_counter_mode")}),
        (_("Statistics"), {"fields": ("counter", "unique_counter")}),
    )

    list_display = ("short_url", "site", "destination_url", "http_status")
    readonly_fields = ("counter", "unique_counter")
    search_fields = ("short_url", "destination_url")


# Double authentification optionnelle
admin.site.login_form = OptionalOTPAdminAuthenticationForm
admin.site.login_template = "admin/login_otp.html"
_admin_get_urls = admin.site.get_urls
admin.site.get_urls = (
    lambda: [
        path("2fa/", admin.site.admin_view(two_factor_view), name="two_factor"),
    ]
    + _admin_get_urls()
)
