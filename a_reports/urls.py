from django.urls import path
from .views import combined_incident_report, enhanced_incident_report

urlpatterns = [
    path("combined/", combined_incident_report, name="combined_incident_report"),
    path("incident/<int:pk>/", enhanced_incident_report, name="enhanced_incident_report"),
]
