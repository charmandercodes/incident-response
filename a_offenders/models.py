from django.conf import settings
from django.db import models
from django.db.models import BooleanField, Case, Value, When
from django.utils import timezone
from django.db.models import Q

# Create your models here.


SEVERITY = (
    ("L", "Low"),
    ("M", "Medium"),
    ("H", "High"),
    ("C", "Critical"),
)

class Offender(models.Model):
    # Basic Info
    name = models.CharField(max_length=255)
    contact_info = models.TextField(blank=True)

    def __str__(self):
        return self.name
    
    # Demographics
    age = models.PositiveIntegerField(null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)  # Alternative to age
    SEX_CHOICES = (
    ('M', 'Male'),
    ('F', 'Female'),
    ('O', 'Other'),
    ('U', 'Unknown'),
)
    sex = models.CharField(max_length=10, choices=SEX_CHOICES, blank=True)
    
    # Physical Description
    height = models.CharField(max_length=20, blank=True)  # e.g., "5'10"" or "178cm"
    weight = models.CharField(max_length=20, blank=True)
    hair_color = models.CharField(max_length=50, blank=True)
    eye_color = models.CharField(max_length=50, blank=True)
    
    # Additional Info
    occupation = models.CharField(max_length=255, blank=True)
    address = models.TextField(blank=True)
    photo = models.ImageField(upload_to='offender_photos/', null=True, blank=True)
    
    # System fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True)  # For additional observations
         
    @property
    def total_warnings(self):
        return self.warnings.count()
    
    @property
    def active_bans(self):
        today = timezone.localdate()
        return self.bans.filter(
         Q(end_date__isnull=True) | Q(end_date__gte=today),
            start_date__lte=today,
            is_active=True,
    )
        return self.bans.filter(is_active=True)

    @property
    def is_currently_banned(self):
        return self.active_bans.exists()


class IncidentOffender(models.Model):
    offender = models.ForeignKey(
        'a_offenders.Offender',
        on_delete=models.CASCADE,
        related_name='incident_links',
    )
    incident = models.ForeignKey(
        'a_incidents.Incident',
        on_delete=models.CASCADE,
        related_name='offender_links',
    )
    role = models.CharField(max_length=50, blank=True)
    linked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("offender", "incident"),
                name="uq_incidentoffender_offender_incident",
            ),
        ]

    def __str__(self):
        return f"{self.offender} ↔ Incident {self.incident_id}"

class Warning(models.Model):
    offender = models.ForeignKey('a_offenders.Offender', on_delete=models.CASCADE, related_name='warnings')
    date = models.DateField(default=timezone.localdate)
    severity = models.CharField(max_length=1, choices=SEVERITY, default="M")
    notes = models.TextField()
    incident = models.ForeignKey('a_incidents.Incident', on_delete=models.SET_NULL, null=True, blank=True, related_name='warnings')
    venue = models.CharField(max_length=255, blank=True)  # your Incident.venue is a CharField now
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"Warning({self.get_severity_display()} → {self.offender.name} @ {self.date})"

class Ban(models.Model):
    offender = models.ForeignKey('a_offenders.Offender', on_delete=models.CASCADE, related_name='bans')
    venue = models.CharField(max_length=255, blank=True)  # keep simple for R1/R2
    reason = models.CharField(max_length=300)
    start_date = models.DateField(default=timezone.localdate)
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    issued_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Ban({self.offender.name} @ {self.venue or 'All venues'})"

    def refresh_active(self):
        today = timezone.localdate()
        self.is_active = self.start_date <= today and (self.end_date is None or self.end_date >= today)
        return self.is_active
    
    def clean(self):
        from django.core.exceptions import ValidationError
        if self.end_date and self.end_date < self.start_date:
            raise ValidationError("End date cannot be before start date.")
