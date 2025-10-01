from io import BytesIO
from collections import Counter, defaultdict
from datetime import datetime

from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.utils.timezone import now

from a_incidents.models import Incident

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph
from reportlab.lib.enums import TA_LEFT


def _pdf_response(filename: str, buffer: BytesIO) -> HttpResponse:
    buffer.seek(0)
    resp = HttpResponse(buffer.read(), content_type="application/pdf")
    
    resp["Content-Disposition"] = f'inline; filename="{filename}"'
    return resp


def _draw_multiline(c: canvas.Canvas, text: str, x: float, y: float, max_width: float, leading: int = 14):
    """Draw word-wrapped text at (x,y)."""
    style = getSampleStyleSheet()["BodyText"]
    style.fontName = "Helvetica"
    style.fontSize = 10
    style.leading = leading
    style.alignment = TA_LEFT
    p = Paragraph(text.replace("\n", "<br/>"), style)
    w, h = p.wrapOn(c, max_width, 9999)
    p.drawOn(c, x, y - h)
    return h


def _page_header(c: canvas.Canvas, title: str, subtitle: str = ""):
    width, height = A4
    c.setFillColor(colors.HexColor("#111827"))  # slate-900
    c.rect(0, height - 26*mm, width, 26*mm, stroke=0, fill=1)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(15*mm, height - 15*mm, title)
    c.setFont("Helvetica", 9)
    c.drawString(15*mm, height - 20*mm, subtitle or now().strftime("%b %d, %Y %I:%M %p"))


def _new_page(c: canvas.Canvas):
    c.showPage()


# ---- Combined PDF ------------------------------------------------------------
def combined_incident_report(request):
    """
    GET /reports/combined/?id=1&id=2...
    Creates a combined PDF with:
      - Selected incidents
      - Totals per venue
      - Severity distribution
      - Warning/Ban counts
    """
    ids = request.GET.getlist("id")
    # Some browsers submit empty string when no checkbox ticked
    ids = [i for i in ids if str(i).strip()]
    if not ids:
        # Generate a one-page PDF telling the user nothing was selected,
        # instead of returning an empty response (blank gray tab).
        buf = BytesIO()
        c = canvas.Canvas(buf, pagesize=A4)
        _page_header(c, "Combined Incident Report", "No incidents selected")
        c.setFillColor(colors.black)
        c.setFont("Helvetica", 12)
        c.drawString(15*mm, 250*mm, "No incidents were selected.")
        c.drawString(15*mm, 242*mm, "Return to the Incidents page, tick some rows, then click Generate Combined PDF.")
        c.save()
        return _pdf_response("combined-empty.pdf", buf)

    # Fetch incidents (keep ordering by created_at desc within selection)
    qs = Incident.objects.filter(id__in=ids).order_by("-created_at")
    if not qs.exists():
        raise Http404("No incidents found for the provided ids")

    # Analytics
    by_venue = Counter([i.venue or "Unknown"] for i in qs)
    by_sev = Counter([getattr(i, "severity", None) for i in qs])
    warn_count = sum(1 for i in qs if getattr(i, "warning", "").lower() == "yes")
    ban_count = sum(1 for i in qs if getattr(i, "ban", "").lower() == "yes")

    # PDF build
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    width, height = A4
    margin = 15*mm
    body_width = width - 2*margin
    y = height - 30*mm

    _page_header(c, "Combined Incident Report", f"{len(qs)} incident(s) selected")

    # Summary panel
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, y, "Summary")
    y -= 7*mm
    c.setFont("Helvetica", 10)
    c.drawString(margin, y, f"Total incidents: {len(qs)}")
    y -= 6*mm
    c.drawString(margin, y, f"Warnings issued: {warn_count}   |   Bans issued: {ban_count}")
    y -= 8*mm

    # Venue totals
    c.setFont("Helvetica-Bold", 11)
    c.drawString(margin, y, "Totals per Venue")
    y -= 6*mm
    c.setFont("Helvetica", 10)
    for venue, count in by_venue.most_common():
        c.drawString(margin + 5*mm, y, f"- {venue}: {count}")
        y -= 5*mm
        if y < 40*mm:
            _new_page(c); _page_header(c, "Combined Incident Report"); y = height - 40*mm

    y -= 4*mm

    # Severity distribution (simple bars)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(margin, y, "Severity Distribution")
    y -= 8*mm
    c.setFont("Helvetica", 10)
    sev_labels = [("Low", 1), ("Medium", 2), ("High", 3)]
    max_val = max(by_sev.values()) if by_sev else 1
    bar_w = (body_width - 30*mm) / len(sev_labels)
    for idx, (label, sev_val) in enumerate(sev_labels):
        val = by_sev.get(sev_val, 0)
        bar_h = 30*mm * (val / max_val if max_val else 0)
        x = margin + idx * (bar_w + 10)
        c.setFillColor(colors.HexColor("#3B82F6"))  # blue-500
        c.rect(x, y - bar_h, bar_w, bar_h, stroke=0, fill=1)
        c.setFillColor(colors.black)
        c.drawString(x, y + 3*mm, f"{label} ({val})")
    y -= 40*mm

    # Details table-like listing
    c.setFont("Helvetica-Bold", 11)
    c.drawString(margin, y, "Incidents")
    y -= 6*mm

    for inc in qs:
        c.setFont("Helvetica-Bold", 10)
        c.drawString(margin, y, f"#{inc.id} — {inc.title}")
        y -= 5*mm
        c.setFont("Helvetica", 9)
        meta = (
            f"Venue: {inc.venue or '-'}   |   "
            f"Severity: {getattr(inc, 'get_severity_display', lambda: inc.severity)()}   |   "
            f"Logged: {inc.created_at:%b %d, %Y %I:%M %p}"
        )
        # For get_severity_display fallback
        if not hasattr(inc, "get_severity_display"):
            meta = (
                f"Venue: {inc.venue or '-'}   |   "
                f"Severity: {getattr(inc, 'severity', '-') }   |   "
                f"Logged: {inc.created_at:%b %d, %Y %I:%M %p}"
            )
        c.drawString(margin + 2*mm, y, meta)
        y -= 5*mm

        descr = inc.description or ""
        y -= _draw_multiline(c, descr, margin + 2*mm, y, body_width - 4*mm, leading=13) + 2*mm

        # New page if needed
        if y < 30*mm:
            _new_page(c)
            _page_header(c, "Combined Incident Report", "Continued…")
            y = height - 40*mm

        y -= 3*mm

    c.save()
    return _pdf_response(f"incidents_combined_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf", buf)


# ---- Enhanced Single-incident PDF -------------------------------------------
def enhanced_incident_report(request, pk: int):
    inc = get_object_or_404(Incident, pk=pk)

    # Historical context
    venue_hist = Incident.objects.filter(venue=inc.venue).exclude(pk=inc.pk)
    offender_hist = Incident.objects.filter(offender_name=inc.offender_name).exclude(pk=inc.pk)

    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    width, height = A4
    margin = 15*mm
    body_width = width - 2*margin
    y = height - 30*mm

    _page_header(c, "Incident Report (Enhanced)", f"Incident #{inc.id}")

    # Header
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, y, inc.title or f"Incident #{inc.id}")
    y -= 7*mm
    c.setFont("Helvetica", 10)
    meta = (
        f"Venue: {inc.venue or '-'}   |   "
        f"Offender: {inc.offender_name or '-'}   |   "
        f"Severity: {getattr(inc, 'get_severity_display', lambda: inc.severity)()}   |   "
        f"Logged: {inc.created_at:%b %d, %Y %I:%M %p}"
    )
    if not hasattr(inc, "get_severity_display"):
        meta = (
            f"Venue: {inc.venue or '-'}   |   "
            f"Offender: {inc.offender_name or '-'}   |   "
            f"Severity: {getattr(inc, 'severity', '-') }   |   "
            f"Logged: {inc.created_at:%b %d, %Y %I:%M %p}"
        )
    c.drawString(margin, y, meta)
    y -= 10*mm

    # Description
    c.setFont("Helvetica-Bold", 11)
    c.drawString(margin, y, "Description")
    y -= 6*mm
    c.setFont("Helvetica", 10)
    y -= _draw_multiline(c, inc.description or "-", margin, y, body_width, leading=14) + 4*mm

    # Historical panels
    c.setFont("Helvetica-Bold", 11)
    c.drawString(margin, y, "Historical Context")
    y -= 7*mm
    c.setFont("Helvetica", 10)
    c.drawString(margin, y, f"Past incidents at this venue: {venue_hist.count()}")
    y -= 5*mm
    c.drawString(margin, y, f"Past incidents for this offender: {offender_hist.count()}")
    y -= 8*mm

    # Small lists (limit to few rows to keep to one page)
    def small_list(title, qs, y_pos):
        c.setFont("Helvetica-Bold", 10)
        c.drawString(margin, y_pos, title)
        y_pos -= 5*mm
        c.setFont("Helvetica", 9)
        for obj in qs.order_by("-created_at")[:8]:
            c.drawString(margin + 3*mm, y_pos, f"- #{obj.id} • {obj.title} • {obj.created_at:%b %d, %Y}")
            y_pos -= 4.5*mm
            if y_pos < 30*mm:
                _new_page(c); _page_header(c, "Incident Report (Enhanced)", f"Incident #{inc.id} (cont.)")
                y_pos = height - 40*mm
        return y_pos - 2*mm

    y = small_list("Venue history (last 8):", venue_hist, y)
    y = small_list("Offender history (last 8):", offender_hist, y)

    # Linked warnings / bans
    c.setFont("Helvetica-Bold", 11)
    c.drawString(margin, y, "Actions")
    y -= 6*mm
    c.setFont("Helvetica", 10)
    c.drawString(margin, y, f"Warning issued: {getattr(inc, 'warning', '-')}")
    y -= 5*mm
    c.drawString(margin, y, f"Ban issued: {getattr(inc, 'ban', '-')}")
    y -= 6*mm

    c.save()
    return _pdf_response(f"incident_{inc.id}_enhanced.pdf", buf)
