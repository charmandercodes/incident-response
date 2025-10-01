from io import BytesIO
from collections import Counter
from datetime import datetime

from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.utils.timezone import now

from a_incidents.models import Incident

# ---- PDF (ReportLab) ---------------------------------------------------------
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph
from reportlab.lib.enums import TA_LEFT


# === drawing helpers ==========================================================
def _pdf_response(filename: str, buffer: BytesIO) -> HttpResponse:
    buffer.seek(0)
    resp = HttpResponse(buffer.read(), content_type="application/pdf")
    resp["Content-Disposition"] = f'inline; filename="{filename}"'
    return resp


def _draw_multiline(
    c: canvas.Canvas,
    text: str,
    x: float,
    y: float,
    max_width: float,
    leading: int = 14,
    size: int = 10,
):
    """Draw word-wrapped text at (x,y) and return height consumed."""
    style = getSampleStyleSheet()["BodyText"]
    style.fontName = "Helvetica"
    style.fontSize = size
    style.leading = leading
    style.alignment = TA_LEFT
    p = Paragraph((text or "").replace("\n", "<br/>"), style)
    w, h = p.wrapOn(c, max_width, 9999)
    p.drawOn(c, x, y - h)
    return h


def _page_header(c: canvas.Canvas, title: str, subtitle: str = ""):
    width, height = A4
    c.setFillColor(colors.HexColor("#0f172a"))  # slate-900
    c.rect(0, height - 26 * mm, width, 26 * mm, stroke=0, fill=1)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(15 * mm, height - 15 * mm, title)
    c.setFont("Helvetica", 9)
    c.drawString(15 * mm, height - 20 * mm, subtitle or now().strftime("%b %d, %Y %I:%M %p"))


def _page_footer(c: canvas.Canvas, page_num: int):
    width, _ = A4
    c.setFillColor(colors.HexColor("#9ca3af"))  # gray-400
    c.setFont("Helvetica", 8)
    c.drawRightString(width - 15 * mm, 12 * mm, f"Page {page_num}")


def _divider(c: canvas.Canvas, x: float, y: float, w: float):
    c.setStrokeColor(colors.HexColor("#e5e7eb"))  # gray-200
    c.setLineWidth(0.6)
    c.line(x, y, x + w, y)


def _new_page(c: canvas.Canvas, title: str, subtitle: str, page_num: int):
    _page_footer(c, page_num)
    c.showPage()
    _page_header(c, title, subtitle)


def _sev_display(inc: Incident) -> str:
    """Return a friendly severity string from the model, fallback to raw value."""
    try:
        d = inc.get_severity_display()
        if d:
            return str(d)
    except Exception:
        pass
    return str(getattr(inc, "severity", "-"))


def _sev_normalize(label: str) -> str:
    """Normalize assorted values to exactly 'Low', 'Medium', or 'High'."""
    s = (label or "").strip().lower()
    if s in {"low", "l", "lo"}:
        return "Low"
    if s in {"medium", "med", "m"}:
        return "Medium"
    if s in {"high", "hi", "h"}:
        return "High"
    # If it doesn't match, drop into 'Medium' to avoid odd buckets.
    return "Medium"


# === Combined PDF =============================================================
def combined_incident_report(request):
    """
    GET /reports/combined/?id=1&id=2...
    Creates a combined PDF with summary, totals, severity bars, and details.
    """
    ids = [s for s in request.GET.getlist("id") if str(s).strip()]
    if not ids:
        buf = BytesIO()
        c = canvas.Canvas(buf, pagesize=A4)
        _page_header(c, "Combined Incident Report", "No incidents selected")
        c.setFillColor(colors.black)
        c.setFont("Helvetica", 12)
        c.drawString(15 * mm, 250 * mm, "No incidents were selected.")
        c.drawString(15 * mm, 242 * mm, "Return to the Incidents page, tick incidents, then click Generate Combined PDF.")
        _page_footer(c, 1)
        c.save()
        return _pdf_response("combined-empty.pdf", buf)

    try:
        id_ints = [int(x) for x in ids]
    except ValueError:
        raise Http404("Invalid incident id in request")

    qs = Incident.objects.filter(id__in=id_ints).order_by("-created_at")
    if not qs.exists():
        raise Http404("No incidents found for the provided ids")

    # --- Analytics ---
    by_venue = Counter((i.venue or "Unknown") for i in qs)

    # Normalize severities into exactly Low/Medium/High buckets.
    by_sev_raw = Counter(_sev_normalize(_sev_display(i)) for i in qs)
    # Always present all three labels, even if zero.
    SEV_LABELS = ["Low", "Medium", "High"]
    by_sev = {lab: by_sev_raw.get(lab, 0) for lab in SEV_LABELS}

    warn_count = sum(1 for i in qs if str(getattr(i, "warning", "")).lower() == "yes")
    ban_count = sum(1 for i in qs if str(getattr(i, "ban", "")).lower() == "yes")

    # --- PDF build ---
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    width, height = A4
    margin = 15 * mm
    body_width = width - 2 * margin
    y = height - 30 * mm
    page = 1

    _page_header(c, "Combined Incident Report", f"{qs.count()} incident(s) selected")

    # Summary
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(margin, y, "Summary")
    y -= 6 * mm
    _divider(c, margin, y, body_width)
    y -= 4 * mm

    c.setFont("Helvetica", 10.5)
    c.drawString(margin, y, f"Total incidents: {qs.count()}")
    y -= 5.2 * mm
    c.drawString(margin, y, f"Warnings: {warn_count}    Bans: {ban_count}")
    y -= 8 * mm

    # Totals per Venue
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, y, "Totals per Venue")
    y -= 6 * mm

    row_h = 6.2 * mm
    col1_w = body_width * 0.7
    col2_w = body_width * 0.3
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(colors.HexColor("#374151"))  # gray-700
    c.drawString(margin + 1 * mm, y, "Venue")
    c.drawRightString(margin + col1_w + col2_w - 1 * mm, y, "Count")
    y -= row_h
    c.setStrokeColor(colors.HexColor("#e5e7eb"))
    c.line(margin, y + 2 * mm, margin + body_width, y + 2 * mm)
    c.setFont("Helvetica", 10)
    c.setFillColor(colors.black)

    for venue, count in by_venue.most_common():
        c.drawString(margin + 1 * mm, y, str(venue))
        c.drawRightString(margin + col1_w + col2_w - 1 * mm, y, str(count))
        y -= row_h
        if y < 60 * mm:
            _new_page(c, "Combined Incident Report", "Continued…", page)
            page += 1
            y = height - 40 * mm

    y -= 4 * mm

    # Severity distribution — ALWAYS show Low/Medium/High (some may be 0)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, y, "Severity Distribution")
    y -= 6 * mm

    max_val = max(by_sev.values()) if any(by_sev.values()) else 1
    max_bar_h = 25 * mm
    bar_w = 22 * mm
    gap = 8 * mm
    labels = ["Low", "Medium", "High"]
    total_w = len(labels) * bar_w + (len(labels) - 1) * gap
    start_x = margin + (body_width - total_w) / 2  # center bars

    # Axis baseline
    c.setStrokeColor(colors.HexColor("#e5e7eb"))
    c.setLineWidth(0.6)
    c.line(margin, y, margin + body_width, y)

    for idx, label in enumerate(labels):
        val = by_sev.get(label, 0)
        bar_h = max_bar_h * (val / max_val if max_val else 0)
        x = start_x + idx * (bar_w + gap)
        # bar
        c.setFillColor(colors.HexColor("#3B82F6"))
        c.rect(x, y - bar_h, bar_w, bar_h, stroke=0, fill=1)
        # value on top (show 0 too for clarity)
        c.setFillColor(colors.HexColor("#111827"))
        c.setFont("Helvetica-Bold", 9)
        c.drawCentredString(x + bar_w / 2, y - bar_h - 4, str(val))
        # label
        c.setFont("Helvetica", 9)
        c.drawCentredString(x + bar_w / 2, y + 4, label)

    y -= (max_bar_h + 16 * mm)

    # Details
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, y, "Incidents")
    y -= 6 * mm
    _divider(c, margin, y, body_width)
    y -= 4 * mm

    for inc in qs:
        c.setFont("Helvetica-Bold", 11)
        c.setFillColor(colors.HexColor("#111827"))
        c.drawString(margin, y, f"#{inc.id} — {inc.title}")
        y -= 5 * mm
        c.setFont("Helvetica", 9.5)
        c.setFillColor(colors.HexColor("#374151"))
        meta = (
            f"Venue: {inc.venue or '-'}   |   "
            f"Severity: {_sev_display(inc)}   |   "
            f"Logged: {inc.created_at:%b %d, %Y %I:%M %p}"
        )
        c.drawString(margin, y, meta)
        y -= 6 * mm
        c.setFillColor(colors.black)

        used = _draw_multiline(c, inc.description or "-", margin, y, body_width, leading=13, size=10)
        y -= used + 6 * mm

        if y < 40 * mm:
            _new_page(c, "Combined Incident Report", "Continued…", page)
            page += 1
            y = height - 40 * mm

    _page_footer(c, page)
    c.save()
    return _pdf_response(f"incidents_combined_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf", buf)


# === Enhanced Single-incident PDF ============================================
def enhanced_incident_report(request, pk: int):
    inc = get_object_or_404(Incident, pk=pk)

    venue_hist = Incident.objects.filter(venue=inc.venue).exclude(pk=inc.pk)
    offender_hist = Incident.objects.filter(offender_name=inc.offender_name).exclude(pk=inc.pk)

    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    width, height = A4
    margin = 15 * mm
    body_width = width - 2 * margin
    y = height - 30 * mm
    page = 1

    _page_header(c, "Incident Report (Enhanced)", f"Incident #{inc.id}")

    # Header
    c.setFont("Helvetica-Bold", 14)
    c.drawString(margin, y, inc.title or f"Incident #{inc.id}")
    y -= 6 * mm
    _divider(c, margin, y, body_width)
    y -= 6 * mm

    c.setFont("Helvetica", 10)
    meta = (
        f"Venue: {inc.venue or '-'}   |   "
        f"Offender: {inc.offender_name or '-'}   |   "
        f"Severity: {_sev_display(inc)}   |   "
        f"Logged: {inc.created_at:%b %d, %Y %I:%M %p}"
    )
    c.drawString(margin, y, meta)
    y -= 10 * mm

    # Description
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, y, "Description")
    y -= 6 * mm
    used = _draw_multiline(c, inc.description or "-", margin, y, body_width, leading=14, size=10.5)
    y -= used + 8 * mm

    # Historical Context
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, y, "Historical Context")
    y -= 6 * mm
    c.setFont("Helvetica", 10)
    c.drawString(margin, y, f"Past incidents at this venue: {venue_hist.count()}")
    y -= 5.2 * mm
    c.drawString(margin, y, f"Past incidents for this offender: {offender_hist.count()}")
    y -= 8 * mm

    def small_list(title, qs, y_pos):
        c.setFont("Helvetica-Bold", 10)
        c.drawString(margin, y_pos, title)
        y_pos -= 4.8 * mm
        c.setFont("Helvetica", 9)
        for obj in qs.order_by("-created_at")[:8]:
            c.drawString(margin + 3 * mm, y_pos, f"- #{obj.id} • {obj.title} • {obj.created_at:%b %d, %Y}")
            y_pos -= 4.4 * mm
            if y_pos < 30 * mm:
                _new_page(c, "Incident Report (Enhanced)", f"Incident #{inc.id} (cont.)", page)
                page += 1
                y_pos = height - 40 * mm
        return y_pos - 2 * mm

    y = small_list("Venue history (last 8):", venue_hist, y)
    y = small_list("Offender history (last 8):", offender_hist, y)

    # Actions
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, y, "Actions")
    y -= 6 * mm
    c.setFont("Helvetica", 10)
    c.drawString(margin, y, f"Warning issued: {getattr(inc, 'warning', '-')}")
    y -= 5.2 * mm
    c.drawString(margin, y, f"Ban issued: {getattr(inc, 'ban', '-')}")
    y -= 6 * mm

    _page_footer(c, page)
    c.save()
    return _pdf_response(f"incident_{inc.id}_enhanced.pdf", buf)
