from django.db import models

# Create your models here.

class Offender(models.Model):
    # Basic Info
    name = models.CharField(max_length=255)
    contact_info = models.TextField(blank=True)
    
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
    
    def __str__(self):
        return self.name
    
    @property
    def total_warnings(self):
        return self.warnings.count()
    
    @property
    def active_bans(self):
        return self.bans.filter(is_active=True)
    
    @property
    def is_currently_banned(self):
        return self.active_bans.exists()