from django.contrib import admin
from .models import Offender, Warning, Ban, IncidentOffender

@admin.register(Offender)
class OffenderAdmin(admin.ModelAdmin):
    list_display = ("name", "total_warnings", "is_currently_banned", "created_at")
    search_fields = ("name", "contact_info", "occupation", "notes")
    list_filter = ("sex", "created_at")

@admin.register(Warning)
class WarningAdmin(admin.ModelAdmin):
    list_display = ("offender", "severity", "date", "venue", "incident", "created_by")
    list_filter = ("severity", "date", "venue")
    search_fields = ("offender__name", "notes")

@admin.register(Ban)
class BanAdmin(admin.ModelAdmin):
    list_display = ("offender", "venue", "start_date", "end_date", "is_active", "reason", "issued_by")
    list_filter = ("venue", "is_active", "start_date")
    search_fields = ("offender__name", "venue", "reason")

@admin.register(IncidentOffender)
class IncidentOffenderAdmin(admin.ModelAdmin):
    list_display = ("offender", "incident", "role", "linked_at")
    search_fields = ("offender__name",)
