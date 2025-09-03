from django.shortcuts import render, redirect
from a_incidents.models import Incident
from .forms import IncidentForm
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User

# Create your views here.

# In your views.py
from django.db.models import Q


def home_page(request):
    incidents = Incident.objects.all().order_by('-created_at')
    
    # Handle search
    search_query = request.GET.get('search', '')
    if search_query:
        incidents = incidents.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(venue__icontains=search_query) |
            Q(offender_name__icontains=search_query)
        )
    
    # Regular request, return full page
    return render(request, 'a_incidents/home.html', {
        'incidents': incidents
    })

@login_required
def create_incident(request):
    if request.method == 'POST':
        form = IncidentForm(request.POST)
        if form.is_valid():
            incident = form.save()
            send_incident_notification(incident, request.user)
            return redirect('home')  # Redirect to a list or detail page
        
    else:
        form = IncidentForm()

    return render(request, 'a_incidents/create_incident.html', {'form': form})

def send_incident_notification(incident, created_by):
    print("NOTIFICATION FUNCTION CALLED!")
    
    # For testing - hardcode your email
    staff_emails = ['rehaan.rahman6@gmail.com']  # Replace with your actual email
    
    print(f"Staff emails found: {staff_emails}")
    
    if not staff_emails:
        return
    
    subject = f"New Incident Reported: {incident.title}"
    
    message = f"""
A new incident has been reported:

Title: {incident.title}
Venue: {incident.venue}
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
            fail_silently=True,
        )
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send notification email: {e}")
# views.py
from django.shortcuts import get_object_or_404, redirect, render
from .models import Incident

@login_required
def delete_incident(request, pk):

    incident = get_object_or_404(Incident, pk=pk)

    if request.method == "POST":  # User confirmed deletion
        incident.delete()
        return redirect('home')  # Go back to list after deleting


@login_required
def update_incident(request, pk):

    incident = get_object_or_404(Incident, pk=pk)

    if request.method == "POST":
        form = IncidentForm(request.POST, instance=incident)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = IncidentForm(instance=incident)
    print(incident.title, incident.description)


    return render(request, 'a_incidents/incident_form.html', {'form': form})


