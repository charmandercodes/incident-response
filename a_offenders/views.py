import csv
from datetime import timedelta
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Count, Prefetch
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from .forms import OffenderForm
from .models import Offender, Warning, Ban, IncidentOffender

def _venue_email_for(venue):
    """Return the best email address from a Venue instance."""
    # Your Venue has `email`, but we’ll be defensive.
    for attr in ("email", "contact_email", "notification_email"):
        addr = getattr(venue, attr, None)
        if addr:
            return addr
    return None

def send_ban_notification(offender, ban, venue):
    """Email the venue with ban details, if venue has an email."""
    to_email = _venue_email_for(venue)
    if not to_email:
        return  # nothing to send to

    venue_label = getattr(venue, "name", "") or (ban.venue or "All venues")
    period = f"{ban.start_date} → {ban.end_date or 'open-ended'}"
    issued_by = (
        (getattr(ban.issued_by, "get_username", lambda: None)() or
         getattr(ban.issued_by, "email", None) or
         "staff")
    )

    subject = f"[Incident Response] Ban issued: {offender.name}"
    body = (
        f"Hello,\n\n"
        f"A ban has been issued.\n\n"
        f"Offender: {offender.name}\n"
        f"Reason: {ban.reason}\n"
        f"Venue: {venue_label}\n"
        f"Duration: {period}\n"
        f"Issued by: {issued_by}\n\n"
        f"Please log in to the system to review.\n"
    )

    send_mail(
        subject=subject,
        message=body,
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
        recipient_list=[to_email],
        fail_silently=False,  # flip to True in prod if you prefer silent failures
    )

def offender_page(request):
    offenders = Offender.objects.all().order_by('-created_at')

    q = request.GET.get("search", "").strip()
    if q:
        offenders = offenders.filter(
            Q(name__icontains=q) |
            Q(contact_info__icontains=q) |
            Q(notes__icontains=q)
        )

    paginator = Paginator(offenders, 5)
    page_number = request.GET.get("page")
    offenders_page = paginator.get_page(page_number)

    return render(request, "a_offenders/home.html", {
        "offenders": offenders_page,
        "search_query": q,
    })

@staff_member_required
def offenders_csv(request):
    resp = HttpResponse(content_type="text/csv")
    resp["Content-Disposition"] = 'attachment; filename="offenders.csv"'
    writer = csv.writer(resp)
    writer.writerow(["Name", "Warnings", "Active bans"])
    for o in Offender.objects.annotate(warn_count=Count("warnings")):
        writer.writerow([o.name, o.warn_count, "Yes" if o.is_currently_banned else "No"])
    return resp

@login_required
def create_offender(request):
    if request.method == "POST":
        form = OffenderForm(request.POST, request.FILES)
        if form.is_valid():
            offender = form.save()

            if form.cleaned_data.get("warning_now"):
                Warning.objects.create(
                    offender=offender,
                    severity=form.cleaned_data.get("warning_severity") or "M",
                    notes="Auto-created at offender creation.",
                    venue="",
                    created_by=request.user,
                )

            if form.cleaned_data.get("ban_now"):
                start = timezone.localdate()
                dur = form.cleaned_data.get("ban_duration") or ""
                end = None if dur in ("", "permanent") else start + timedelta(days=int(dur))

                ban = Ban.objects.create(
                    offender=offender,
                    reason=form.cleaned_data.get("ban_reason") or "Auto-created at offender creation.",
                    venue="",  # your Ban.venue is a CharField label
                    start_date=start,
                    end_date=end,
                    issued_by=request.user,
                )
                if form.cleaned_data.get("notify_venue") and form.cleaned_data.get("venue_to_notify"):
                    send_ban_notification(offender, ban, form.cleaned_data["venue_to_notify"])

            return redirect("offender-home")
    else:
        form = OffenderForm()
    return render(request, "a_offenders/create_offender.html", {"form": form})

@login_required
def update_offender(request, pk):
    offender = get_object_or_404(Offender, pk=pk)
    if request.method == "POST":
        form = OffenderForm(request.POST, request.FILES, instance=offender)
        if form.is_valid():
            offender = form.save()

            if form.cleaned_data.get("warning_now"):
                Warning.objects.create(
                    offender=offender,
                    severity=form.cleaned_data.get("warning_severity") or "M",
                    notes="Auto-created during offender update.",
                    venue="",
                    created_by=request.user,
                )

            if form.cleaned_data.get("ban_now"):
                start = timezone.localdate()
                dur = form.cleaned_data.get("ban_duration") or ""
                end = None if dur in ("", "permanent") else start + timedelta(days=int(dur))
                Ban.objects.create(
                    offender=offender,
                    reason=form.cleaned_data.get("ban_reason") or "Auto-created during offender update.",
                    venue="",
                    start_date=start,
                    end_date=end,
                    issued_by=request.user,
                )
                if form.cleaned_data.get("notify_venue") and form.cleaned_data.get("venue_to_notify"):
                    send_ban_notification(offender, ban, form.cleaned_data["venue_to_notify"])

            return redirect("offender-home")
    else:
        form = OffenderForm(instance=offender)
    return render(request, "a_offenders/update_offender.html", {"form": form, "offender": offender})

def offender_detail(request, pk):
    offender = get_object_or_404(
        Offender.objects
        .prefetch_related(
            Prefetch('warnings', queryset=Warning.objects.order_by('-date', '-created_at')),
            Prefetch('bans', queryset=Ban.objects.order_by('-created_at')),
            Prefetch('incident_links', queryset=IncidentOffender.objects.select_related('incident').order_by('-linked_at')),
        )
        .annotate(warnings_count=Count('warnings')),
        pk=pk
    )

    context = {
        "offender": offender,
        "active_bans": offender.active_bans,
        "warnings": offender.warnings.all(),
        "bans": offender.bans.all(),
        "incident_links": offender.incident_links.all(),
    }
    return render(request, "a_offenders/detail.html", context)

@login_required
def delete_offender(request, pk):
    offender = get_object_or_404(Offender, pk=pk)
    if request.method == "POST":
        offender.delete()
        return redirect("offender-home")
    return redirect("offender-home")
