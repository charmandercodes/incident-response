from django.db import models
from a_venues.models import Venue
from a_offenders.models import Offender

class Incident(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()

    INCIDENT_TYPE_CHOICES = [
        ('theft', 'Theft'),
        ('assault', 'Assault'),
        ('vandalism', 'Vandalism'),
        ('other', 'Other'),
    ]
    incident_type = models.CharField(
        max_length=50,
        choices=INCIDENT_TYPE_CHOICES,
        default='other'
    )

    # Venue as ForeignKey
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE)

    # Single main offender (optional)
    offender = models.ForeignKey(
        Offender,
        on_delete=models.CASCADE,
        related_name='primary_incidents',
        null=True,
        blank=True
    )

    # Multiple offenders (optional)
    offenders = models.ManyToManyField(
        Offender,
        related_name='group_incidents',
        blank=True
    )

    # Severity
    SEVERITY_CHOICES = [
        (1, "Low"),
        (2, "Medium-Low"),
        (3, "Medium"),
        (4, "Medium-High"),
        (5, "High"),
    ]
    severity = models.IntegerField(choices=SEVERITY_CHOICES, default=3)

    # Warning & Ban
    WARNING_CHOICES = [
        ("no", "No"),
        ("yes", "Yes"),
    ]
    warning = models.CharField(max_length=20, choices=WARNING_CHOICES, default="no")

    BAN_CHOICES = [
        ("no", "No"),
        ("yes", "Yes"),
    ]
    ban = models.CharField(max_length=20, choices=BAN_CHOICES, default="no")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Incident: {self.title} at {self.venue}"
