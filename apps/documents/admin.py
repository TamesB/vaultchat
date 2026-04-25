from django.contrib import admin

from .models import Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("filename", "organization", "uploaded_by", "status", "created_at")
    list_filter = ("status", "organization")
    search_fields = ("filename",)
