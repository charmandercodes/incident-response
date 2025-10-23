try:
    from a_notifications.models import NotificationLog
except Exception:
    NotificationLog = None
# a_notifications/utils.py
"""
Integrates F103 (Ban Records & Alerts) + F104 (Notification Integrations)
into existing notification utilities without changing structure.
"""
from dataclasses import dataclass
from typing import Optional
from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
from a_offenders.models import Ban, Offender
from a_venues.models import Venue
from a_notifications.models import NotificationLog


# -------------------------------
# Support data structure
# -------------------------------
@dataclass
class SendResult:
    ok: bool
    error: Optional[str] = None


# -------------------------------
# Centralized logging function
# -------------------------------
def _log(kind: str, status: str, to_email: str, subject: str, body: str,
         ban: Optional[Ban] = None, offender: Optional[Offender] = None, venue: Optional[Venue] = None,
         error: Optional[str] = None):
    """
    Creates a persistent record of all notifications sent for audit trail.
    F103 integration: links Ban → Notification for alert badges & analytics.
    """
    NotificationLog.objects.create(
        ban=ban,
        offender=offender,
        venue=venue,
        type=kind,
        status=status,
        to_email=to_email,
        subject=subject,
        body_preview=body[:240],
        error=error
    )


# -------------------------------
# Email send helper
# -------------------------------
def _send(to_email: str, subject: str, body: str) -> SendResult:
    """Base email sender; returns success/failure for logging."""
    try:
        send_mail(
            subject,
            body,
            getattr(settings, 'DEFAULT_FROM_EMAIL', None),
            [to_email],
            fail_silently=False
        )
        return SendResult(ok=True)
    except Exception as e:
        return SendResult(ok=False, error=str(e))

# -------------------------------
# 0 Send Ban Notifications
# -------------------------------
def send_ban_notification(offender, ban, venue_name=None):
    """
    Sends a notification when a ban is created.
    Logs the event to NotificationLog.
    If venue_name is provided, it means we're notifying a specific venue.
    """
    subject = f"Ban issued for {offender.name}"
    body = f"{offender.name} has been banned for the following reason: {ban.reason}"
    if venue_name:
        body += f"\n\nVenue Notified: {venue_name}"

    try:
        # Example of logging (instead of actually sending emails for now)
        NotificationLog.objects.create(
            type="BAN_NOTIFICATION",
            status="SENT",
            to_email="venue@example.com",  # placeholder
            subject=subject,
            body_preview=body[:200],
            offender=offender,
            ban=ban,
        )
        print(f"✅ Ban notification logged for {offender.name}")
        return True
    except Exception as e:
        NotificationLog.objects.create(
            type="BAN_NOTIFICATION",
            status="FAILED",
            error=str(e),
            offender=offender,
            ban=ban,
        )
        print(f"⚠️ Failed to log ban notification: {e}")
        return False
# -------------------------------
# 1️ Venue ban notification
# -------------------------------
@transaction.atomic
def send_venue_ban(ban: Ban):
    """
    Notifies a venue when an offender under its management is banned.
    F104 integration: this is triggered when Ban model is saved with status='active'.
    """
    venue = getattr(ban, 'venue_obj', None)
    to_email = getattr(venue, 'email', None) or ''
    if not to_email:
        _log(
            'VENUE_BAN_ISSUED', 'FAILED', '(none)', 'Missing venue email', 'No body',
            ban=ban, venue=venue, error='missing_email'
        )
        return

    subject = f"[Incident Response] Ban issued: {ban.offender.name}"
    period = f"{ban.start_date} → {ban.end_date or 'open-ended'}"
    body = (
        f"Hello {venue.name if venue else 'Venue'},\n\n"
        f"A ban has been issued.\n"
        f"Offender: {ban.offender.name}\n"
        f"Reason: {ban.reason}\n"
        f"Duration: {period}\n"
        f"Issued by: {getattr(ban.issued_by, 'email', 'staff')}\n\n"
        f"Please ensure staff are aware of the active ban."
    )

    res = _send(to_email, subject, body)
    _log(
        'VENUE_BAN_ISSUED',
        'SENT' if res.ok else 'FAILED',
        to_email, subject, body,
        ban=ban, venue=venue, error=res.error
    )

    # --- F103 addition: update venue badge / analytics ---
    if res.ok:
        # increment badge counter for active bans (pseudo logic)
        if hasattr(venue, 'active_ban_count'):
            venue.active_ban_count += 1
            venue.save(update_fields=['active_ban_count'])


# -------------------------------
# 2️ Offender ban notification
# -------------------------------
@transaction.atomic
def send_offender_ban(ban: Ban):
    """
    Notifies the offender about their ban (F104).
    Includes F103 integration to update badge/counter on offender profile.
    """
    offender = ban.offender
    to_email = getattr(offender, 'email', None) or ''
    if not to_email:
        _log(
            'OFFENDER_BAN_ISSUED', 'FAILED', '(none)',
            'Missing offender email', 'No body',
            ban=ban, offender=offender, error='missing_email'
        )
        return

    subject = "Notice of Ban"
    period = f"{ban.start_date} → {ban.end_date or 'open-ended'}"
    body = (
        f"Hello {offender.name},\n\n"
        f"You have been banned.\n"
        f"Reason: {ban.reason}\n"
        f"Duration: {period}\n\n"
        f"Please contact administration if you believe this was in error."
    )

    res = _send(to_email, subject, body)
    _log(
        'OFFENDER_BAN_ISSUED',
        'SENT' if res.ok else 'FAILED',
        to_email, subject, body,
        ban=ban, offender=offender, error=res.error
    )

    # --- F103 addition: update offender badge counter ---
    if res.ok and hasattr(offender, 'ban_badge_count'):
        offender.ban_badge_count += 1
        offender.save(update_fields=['ban_badge_count'])


# -------------------------------
# 3️ Ban expiry alerts (admins)
# -------------------------------
def send_expiry_alert(ban: Ban, threshold_label: str):
    """
    Alerts admins when a ban is nearing expiry (F103).
    threshold_label ∈ {'T-3','T-0'} for 3-day and same-day reminders.
    """
    for admin_email in getattr(settings, 'STAFF_ALERT_EMAILS', []):
        subject = f"[Ban Expiry {threshold_label}] {ban.offender.name}"
        period = f"{ban.start_date} → {ban.end_date}"
        body = (
            f"Ban for {ban.offender.name} is reaching expiry.\n"
            f"Ends: {ban.end_date}\nReason: {ban.reason}\n\n"
            f"Please review and renew if necessary."
        )
        res = _send(admin_email, subject, body)
        _log(
            f'BAN_EXPIRY_{threshold_label.replace("-", "")}',
            'SENT' if res.ok else 'FAILED',
            admin_email, subject, body,
            ban=ban, offender=ban.offender, error=res.error
        )
