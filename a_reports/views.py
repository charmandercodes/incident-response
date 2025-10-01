from typing import List
from django.views import View
from django.http import HttpRequest, HttpResponse, Http404
from django.shortcuts import render, get_object_or_404
from django.db.models import Count

from a_incidents.models import Incident


def _render_to_pdf_like(html: str) -> HttpResponse:
    """
    Minimal stand-in so this works everywhere (incl. Azure Pipelines).
    It returns a PDF content-type with the HTML payload.
    Swap for WeasyPrint/ReportLab later without changing the callers.
    """
    resp = HttpResponse(html, content_type="application/pdf")
    resp["Content-Disposition"] = 'inline; filename="report.pdf"'
    return resp


class CombinedIncidentsReportView(View):
    """
    /reports/combined/?id=1&id=2&id=7
    Produces a single "PDF" response (content-type) with summaries across incidents.
    """

    template_name = "a_reports/combined_incidents_report.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        ids: List[str] = request.GET.getlist("id")
        if not ids:
            # Render a friendly page instead of 404 if accessed without IDs
            return render(request, self.template_name, {"incidents": [], "by_venue": [], "by_type": [], "repeat_offenders": []})

        incidents = Incident.objects.filter(id__in=ids)

        # Totals per venue (venue is a CharField)
        by_venue = (
            incidents.exclude(venue__isnull=True)
            .exclude(venue__exact="")
            .values("venue")
            .annotate(total=Count("id"))
            .order_by("-total")
        )

        # Totals per incident "type" if such a field exists (guarded)
        by_type = []
        if hasattr(Incident, "type"):
            by_type = incidents.values("type").annotate(total=Count("id")).order_by("-total")

        # Repeat offenders if you later wire M2M: guarded to not break anything
        repeat_offenders = []

        ctx = {
            "incidents": incidents,
            "by_venue": by_venue,
            "by_type": by_type,
            "repeat_offenders": repeat_offenders,
        }
        html = render(request, self.template_name, ctx).content.decode("utf-8")
        return _render_to_pdf_like(html)


class EnhancedIncidentReportView(View):
    """
    /reports/incident/<pk>/enhanced/
    Single-incident report with simple historical context (same venue / same offender_name).
    """

    template_name = "a_reports/enhanced_incident_report.html"

    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        incident = get_object_or_404(Incident, pk=pk)

        # History for the same venue (string match)
        venue_history = (
            Incident.objects.filter(venue=incident.venue)
            .exclude(pk=incident.pk)
            .order_by("-created_at")[:10]
            if incident.venue
            else []
        )

        # History for same offender_name (string match, because your model has that field)
        offender_history = (
            Incident.objects.filter(offender_name=incident.offender_name)
            .exclude(pk=incident.pk)
            .order_by("-created_at")[:10]
            if incident.offender_name
            else []
        )

        ctx = {
            "incident": incident,
            "venue_history": venue_history,
            "offender_history": offender_history,
            "venue_history_count": len(venue_history) if venue_history else 0,
            "offender_history_count": len(offender_history) if offender_history else 0,
        }
        html = render(request, self.template_name, ctx).content.decode("utf-8")
        return _render_to_pdf_like(html)
