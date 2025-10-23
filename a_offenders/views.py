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

# notification helpers (from your notifications app)
from a_notifications.utils import send_venue_ban, send_offender_ban, send_ban_notification


def _venue_email_for(venue):
    """Return the best email address from a Venue instance (defensive)."""
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
        fail_silently=False,
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

            # Create warning if requested
            if form.cleaned_data.get("warning_now"):
                Warning.objects.create(
                    offender=offender,
                    severity=form.cleaned_data.get("warning_severity") or "M",
                    notes="Auto-created at offender creation.",
                    venue="",
                    created_by=request.user,
                )

            # Create ban if requested
            if form.cleaned_data.get("ban_now"):
                start = timezone.localdate()
                dur = form.cleaned_data.get("ban_duration") or ""
                end = None if dur in ("", "permanent") else start + timedelta(days=int(dur))

                # venue_to_notify is a ModelChoiceField -> returns a Venue instance or None
                venue_obj = form.cleaned_data.get("venue_to_notify")

                # IMPORTANT:
                # If your Ban.venue is defined as a ForeignKey to a_venues.Venue, set venue=venue_obj.
                # If Ban.venue is a CharField (current), store a readable label (venue_obj.name) and
                # attach venue_obj to the ban instance for runtime use in notifications.
                ban_kwargs = {
                    "offender": offender,
                    "reason": form.cleaned_data.get("ban_reason") or "Auto-created at offender creation.",
                    "start_date": start,
                    "end_date": end,
                    "issued_by": request.user,
                }

                # Try to detect whether Ban.venue is a FK by checking model field
                try:
                    ban_field = Ban._meta.get_field("venue")
                    is_fk = ban_field.get_internal_type() in ("ForeignKey",)
                except Exception:
                    is_fk = False

                if is_fk:
                    # If venue is a FK, store the object directly
                    ban_kwargs["venue"] = venue_obj
                else:
                    # Keep storing the label (existing behaviour) to avoid migration,
                    # but attach the Venue object at runtime for notifications
                    ban_kwargs["venue"] = venue_obj.name if venue_obj else ""

                ban = Ban.objects.create(**ban_kwargs)

                # If we stored a label (CharField case), attach full object for notifications
                if not is_fk and venue_obj:
                    # transient runtime attribute used by send_venue_ban()
                    ban.venue_obj = venue_obj

                # Only send a venue notification if requested and venue chosen
                if form.cleaned_data.get("notify_venue") and venue_obj:
                    # Prefer the centralised notifier (works with FK or with ban.venue_obj)
                    send_venue_ban(ban)

                # Notify the offender (best-effort; your send_offender_ban should be robust)
                send_offender_ban(ban)

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

                venue_obj = form.cleaned_data.get("venue_to_notify")

                ban_kwargs = {
                    "offender": offender,
                    "reason": form.cleaned_data.get("ban_reason") or "Auto-created during offender update.",
                    "start_date": start,
                    "end_date": end,
                    "issued_by": request.user,
                }

                try:
                    ban_field = Ban._meta.get_field("venue")
                    is_fk = ban_field.get_internal_type() in ("ForeignKey",)
                except Exception:
                    is_fk = False

                if is_fk:
                    ban_kwargs["venue"] = venue_obj
                else:
                    ban_kwargs["venue"] = venue_obj.name if venue_obj else ""

                ban = Ban.objects.create(**ban_kwargs)

                if not is_fk and venue_obj:
                    ban.venue_obj = venue_obj

                if form.cleaned_data.get("notify_venue") and venue_obj:
                    send_venue_ban(ban)

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
