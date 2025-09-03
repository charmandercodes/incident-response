from django.urls import include, path
from .views import IncidentPDFView

urlpatterns = [
    path('incident/<int:pk>/pdf/', IncidentPDFView.as_view(), name='incident_pdf_report'),
]