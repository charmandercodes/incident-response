from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

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

    # Authentication URLs using your a_auth login template
    path("login/", auth_views.LoginView.as_view(template_name="a_auth/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
