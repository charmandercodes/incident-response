from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("", include("a_incidents.urls")),
    path("venues/", include("a_venues.urls")),
    path("admin/", admin.site.urls),
    path("auth/", include("a_auth.urls")),
    path("logs/", include("a_logs.urls")),
    path("reports/", include("a_reports.urls")),
    path("offenders/", include("a_offenders.urls")),
    path("notifications/", include("a_notifications.urls")),
    path("analytics/", include("a_analytics.urls")),
    
    path("accounts/", include("django.contrib.auth.urls")),
]
