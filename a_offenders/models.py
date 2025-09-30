from django.db import models
from django.utils import timezone
from django.conf import settings
# Create your models here.

class Offender(models.Model):
    # Basic Info
    name = models.CharField(max_length=255)
    contact_info = models.TextField(blank=True)

    def __str__(self):
        return self.name
    
    # Demographics
    age = models.PositiveIntegerField(null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)  # Alternative to age
    sex = models.CharField(
        max_length=10, 
        choices=[
            ('M', 'Male'),
            ('F', 'Female'),
            ('O', 'Other'),
            ('U', 'Unknown')
        ],
        blank=True
    )
    
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
        ids = list(self.bans.values_list('id', flat=True))
        self.bans.filter(id__in=ids).update(
            is_active=dj_models.Case(
                dj_models.When(end_date__lt=timezone.localdate(), then=dj_models.Value(False)),
                default=dj_models.Value(True),
                output_field=dj_models.BooleanField(),
            )
        )
        return self.bans.filter(is_active=True)

    @property
    def is_currently_banned(self):
        return self.active_bans.exists()
    

    class IncidentOffender(models.Model):
    offender = models.ForeignKey(
        'a_offenders.Offender',
        on_delete=modsels.CASCADE,
        related_name='incident_links'
    )
    incident = models.ForeignKey(
        'a_incidents.Incident',
        on_delete=models.CASCADE,
        related_name='offender_links'
    )
    role = models.CharField(max_length=50, blank=True)
    linked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('offender', 'incident')

    def __str__(self):
        return f"{self.offender} ↔ Incident {self.incident_id}"
    
    SEVERITY = (
    ("L", "Low"),
    ("M", "Medium"),
    ("H", "High"),
    ("C", "Critical"),
)

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
    