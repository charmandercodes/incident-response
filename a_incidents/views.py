from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q, QuerySet

from a_incidents.models import Incident
from .forms import IncidentForm


def _apply_filters_and_sorting(request, qs: QuerySet) -> QuerySet:
    search_query = request.GET.get("search", "").strip()
    if search_query:
        qs = qs.filter(
            Q(title__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(venue__icontains=search_query)
            | Q(offender_name__icontains=search_query)
        )

    venue_params = [v.strip() for v in request.GET.getlist("venue") if v.strip()]
    if venue_params:
        qs = qs.filter(venue__in=venue_params)

    sort = request.GET.get("sort")
    if sort == "severity_asc":
        qs = qs.order_by("severity", "-created_at")
    elif sort == "severity_desc":
        qs = qs.order_by("-severity", "-created_at")
    else:
        qs = qs.order_by("-created_at")

    return qs


def home_page(request):
    incidents = _apply_filters_and_sorting(request, Incident.objects.all())

    venues = (
        Incident.objects.exclude(venue__isnull=True)
        .exclude(venue__exact="")
        .values_list("venue", flat=True)
        .distinct()
        .order_by("venue")
    )

    sel_venues = request.GET.getlist("venue")
    search = request.GET.get("search", "")
    sort = request.GET.get("sort", "")

    return render(
        request,
        "a_incidents/home.html",
        {
            "incidents": incidents,
            "venues": venues,
            "sel_venues": sel_venues,
            "search": search,
            "sort": sort,
        },
    )


@login_required
def create_incident(request):
    if request.method == "POST":
        form = IncidentForm(request.POST)
        if form.is_valid():
            incident = form.save()
            send_incident_notification(incident, request.user)
            return redirect("home")
        # fallthrough to re-render with errors
    else:
        form = IncidentForm()
    return render(request, "a_incidents/create_incident.html", {"form": form})


def send_incident_notification(incident, created_by):
    staff_emails = ["rehaan.rahman6@gmail.com"]
    if not staff_emails:
        return
    subject = f"New Incident Reported: {incident.title}"
    message = f"""
A new incident has been reported:

Title: {incident.title}
Venue: {incident.venue}
Severity: {incident.get_severity_display() if hasattr(incident, 'get_severity_display') else getattr(incident, 'severity', '-') }
Reported by: {getattr(created_by, 'username', 'unknown')}
Date: {incident.created_at.strftime('%B %d, %Y at %I:%M %p') if hasattr(incident, 'created_at') else ''}

Description:
{incident.description}

Please log in to the system to review the full details.
    """.strip()
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=staff_emails,
            fail_silently=True,
        )
    except Exception:
        pass


@login_required
def delete_incident(request, pk):
    incident = get_object_or_404(Incident, pk=pk)
    if request.method == "POST":
        incident.delete()
        return redirect("home")
    return render(request, "a_incidents/confirm_delete.html", {"incident": incident})


@login_required
def update_incident(request, pk):
    incident = get_object_or_404(Incident, pk=pk)
    if request.method == "POST":
        form = IncidentForm(request.POST, instance=incident)
        if form.is_valid():
            form.save()
            return redirect("home")
        # fallthrough to show errors
    else:
        form = IncidentForm(instance=incident)
    return render(request, "a_incidents/incident_form.html", {"form": form, "incident": incident})
