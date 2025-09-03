from django.shortcuts import render
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User

# Create your views here.


def send_incident_notification(incident, created_by):
    """Send email notification about new incident"""
    
    # Get all staff users to notify
    staff_users = User.objects.filter(is_staff=True).exclude(id=created_by.id)
    staff_emails = [user.email for user in staff_users if user.email]
    
    if not staff_emails:
        return  # No one to notify
    
    subject = f"New Incident Reported: {incident.title}"
    
    message = f"""
A new incident has been reported:

Title: {incident.title}
Venue: {incident.venue.name if incident.venue else 'Not specified'}
Reported by: {created_by.username}
Date: {incident.created_at.strftime('%B %d, %Y at %I:%M %p')}

Description:
{incident.description}

Please log in to the system to review the full details.
    """
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=staff_emails,
            fail_silently=True,  # Don't break the app if email fails
        )
    except Exception as e:
        # Log the error but don't break the incident creation
        print(f"Failed to send notification email: {e}")