from django.contrib import admin

from .models import Chat, Message


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ("id", "organization", "created_by", "title", "created_at")
    list_filter = ("organization",)
    search_fields = ("title", "created_by__email")


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "organization", "chat", "role", "created_at")
    list_filter = ("organization", "role")
    search_fields = ("content",)
