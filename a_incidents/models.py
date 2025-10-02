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

    venue = models.ForeignKey(Venue, on_delete=models.CASCADE)
    
    # Keep existing ForeignKey (someone else's part)
    offender = models.ForeignKey(
        Offender,
        on_delete=models.CASCADE,
        related_name='primary_incidents',  # <-- change related_name to avoid clash
        null=True,
        blank=True
    )

    # Your ManyToManyField for multiple offenders
    offenders = models.ManyToManyField(
        Offender,
        related_name='incidents',  # <-- make sure this is different from above
        blank=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    WARNING_CHOICES = [
        ('no', 'No'),
        ('yes', 'Yes'),
    ]
    warning = models.CharField(max_length=20, choices=WARNING_CHOICES, default='no')
    
    BAN_CHOICES = [
        ('no', 'No'),
        ('yes', 'Yes'),
    ]
    ban = models.CharField(max_length=20, choices=BAN_CHOICES, default='no')
    
    def __str__(self):
        return f"Incident: {self.title} at {self.venue}"
