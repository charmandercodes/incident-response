from django.db import models

# Create your models here.


class Incident(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    offender_name = models.CharField(max_length=255)
    venue = models.CharField(max_length=255)


    def __str__(self):
        return f"Incident: {self.title}" 

