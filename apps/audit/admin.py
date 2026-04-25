from django.contrib import admin

from .models import AuditEvent


@admin.register(AuditEvent)
class AuditEventAdmin(admin.ModelAdmin):
    list_display = ("event_type", "organization", "user", "created_at")
    list_filter = ("event_type", "organization")
    search_fields = ("event_type",)

