# a_notifications/admin.py
from django.contrib import admin
from .models import NotificationLog

@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = ('type', 'status', 'to_email', 'created_at')
    search_fields = ('to_email', 'subject', 'body_preview')
    list_filter = ('type', 'status', 'created_at')
