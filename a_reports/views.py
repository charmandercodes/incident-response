from django.shortcuts import render

from django_weasyprint import WeasyTemplateResponseMixin
from django.views.generic import DetailView
from a_incidents.models import Incident

class IncidentPDFView(WeasyTemplateResponseMixin, DetailView):
    model = Incident
    template_name = 'a_reports/incident_pdf.html'
    pdf_attachment = True
    pdf_filename = 'incident_report.pdf'
# Create your views here.
