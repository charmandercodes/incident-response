from django.db import models
from django.conf import settings
from a_offenders.models import Offender
from a_venues.models import Venue
from a_offenders.models import Ban  # adjust if Ban is in another app

class NotificationLog(models.Model):
    # kind/type e.g. 'VENUE_BAN_ISSUED', 'OFFENDER_BAN_ISSUED'
    type = models.CharField(max_length=64)
    status = models.CharField(max_length=16)  # 'SENT' / 'FAILED'
    to_email = models.EmailField(null=True, blank=True)
    subject = models.CharField(max_length=255, blank=True)
    body_preview = models.TextField(blank=True)
    error = models.TextField(blank=True, null=True)

    # optional links
    ban = models.ForeignKey(Ban, null=True, blank=True, on_delete=models.SET_NULL)
    offender = models.ForeignKey(Offender, null=True, blank=True, on_delete=models.SET_NULL)
    venue = models.ForeignKey(Venue, null=True, blank=True, on_delete=models.SET_NULL)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.type} -> {self.to_email} ({self.status})"
