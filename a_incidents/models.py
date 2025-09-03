from django.db import models

# Create your models here.


class Incident(models.Model):
    # Incident related fields
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    offender_name = models.CharField(max_length=255)
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
    