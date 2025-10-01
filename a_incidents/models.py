from django.db import models


class Incident(models.Model):
    # Incident fields
    title = models.CharField(max_length=255)
    description = models.TextField()

    # NEW: sortable severity (1=Low .. 5=High)
    SEVERITY_CHOICES = [
        (1, "Low"),
        (2, "Medium-Low"),
        (3, "Medium"),
        (4, "Medium-High"),
        (5, "High"),
    ]
    severity = models.IntegerField(choices=SEVERITY_CHOICES, default=3)

    # When
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Offender linkage (kept as-is from your repo)
    offender = models.ForeignKey(
        "a_offenders.Offender",
        on_delete=models.CASCADE,
        related_name="incidents",
        null=True,
        blank=True,
    )
    # Keep old field for compatibility with your form
    offender_name = models.CharField(max_length=255, blank=True)

    # Venue is a simple string in the current codebase
    venue = models.CharField(max_length=255)

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

    def __str__(self):
        return f"Incident: {self.title}"
