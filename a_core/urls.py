"""
URL configuration for a_core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('', include('a_incidents.urls')),
    path('venues/', include('a_venues.urls')),
    path('admin/', admin.site.urls),
    path('auth/', include('a_auth.urls')),
    path('logs/', include('a_logs.urls')),
    path('reports/', include('a_reports.urls')),
    path('offenders/', include('a_offenders.urls')),
    path('notifications/', include('a_notifications.urls')),
    path('analytics/', include('a_analytics.urls')),
]
