from django.contrib import admin

from .models import DocumentChunk


@admin.register(DocumentChunk)
class DocumentChunkAdmin(admin.ModelAdmin):
    list_display = ("id", "organization", "document", "created_at")
    list_filter = ("organization",)
    search_fields = ("content",)