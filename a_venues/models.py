from django.db import models

# Create your models here.


class Venue(models.Model):
    # Basic Info
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Location Details
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=20)
    
    # Contact Information
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    manager_name = models.CharField(max_length=255, blank=True)
    
    # Operational Details
    venue_type = models.CharField(max_length=50, choices=[
        ('shopping_center', 'Shopping Center'),
        ('mall', 'Mall'),
        ('office_building', 'Office Building'),
        ('retail_store', 'Retail Store'),
        ('parking_garage', 'Parking Garage'),
        ('other', 'Other'),
    ], default='shopping_center')
    
    capacity = models.IntegerField(null=True, blank=True, help_text="Maximum occupancy")
    operating_hours = models.CharField(max_length=255, blank=True, help_text="e.g., Mon-Sun 9AM-9PM")
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']