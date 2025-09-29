from django.db import models

class Incident(models.Model):
    # Incident related fields
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Foreign Key to Offender model
    offender = models.ForeignKey(
        'a_offenders.Offender',  # Adjust app name if different
        on_delete=models.CASCADE,
        related_name='incidents',
        null=True,  # Temporarily allow null for migration
        blank=True
    )
    
    # Keep old field temporarily for data migration
    offender_name = models.CharField(max_length=255, blank=True)
    
    venue = models.CharField(max_length=255)

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
        return f"Incident: {self.title}"