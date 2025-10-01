from django.urls import path
from .views import CombinedIncidentsReportView, EnhancedIncidentReportView

urlpatterns = [
    path("combined/", CombinedIncidentsReportView.as_view(), name="combined_incident_report"),
    path("incident/<int:pk>/enhanced/", EnhancedIncidentReportView.as_view(), name="enhanced_incident_report"),
]
