from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()

def send_incident_notification(incident, created_by):
    """
    Email staff users (excluding the reporter) when a new incident is created.
    """
    staff_emails = list(
        User.objects.filter(is_staff=True)
        .exclude(id=getattr(created_by, "id", None))
        .values_list("email", flat=True)
    )
    staff_emails = [e for e in staff_emails if e]

    if not staff_emails:
        return

    # venue string (works even if it's a CharField or FK)
    venue_str = ""
    if hasattr(incident, "venue") and incident.venue:
        venue_str = getattr(incident.venue, "name", str(incident.venue))
    else:
        venue_str = "Not specified"

    subject = f"[Incident] New Incident Reported: {getattr(incident, 'title', 'Untitled')}"
    created_str = getattr(incident, "created_at", None)
    created_fmt = created_str.strftime("%B %d, %Y at %I:%M %p") if created_str else "(time not set)"

    message = (
        "A new incident has been reported:\n\n"
        f"Title: {getattr(incident, 'title', 'Untitled')}\n"
        f"Venue: {venue_str}\n"
        f"Reported by: {getattr(created_by, 'username', 'unknown')}\n"
        f"Date: {created_fmt}\n\n"
        f"Description:\n{getattr(incident, 'description', '').strip()}\n\n"
        "Please log in to the system to review the full details."
    )

    send_mail(
        subject=subject,
        message=message,
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
        recipient_list=staff_emails,
        fail_silently=True,  # don’t crash on email errors in R1
    )
