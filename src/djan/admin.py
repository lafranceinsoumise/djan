from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from djan.models import Redirection


@admin.register(Redirection)
class RedirectionAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {"fields": ("site", "short_url", "destination_url", "http_status")}),
        (_("Parameters"), {"fields": ("params_mode", "unique_counter_mode")}),
        (_("Statistics"), {"fields": ("counter", "unique_counter")}),
    )

    list_display = ("short_url", "site", "destination_url", "http_status")
    readonly_fields = ("counter", "unique_counter")
