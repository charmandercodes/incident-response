from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q
from .models import Incident
from .forms import IncidentForm


# ----------------------------
# Home / Incident List View
# ----------------------------
def home_page(request):
    incidents = Incident.objects.all().order_by('-created_at')

    # Handle search
    search_query = request.GET.get('search', '')
    if search_query:
        incidents = incidents.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(venue__icontains=search_query) |
            Q(offender__name__icontains=search_query)  # Search on ForeignKey
        ).distinct()

    return render(request, 'a_incidents/home.html', {
        'incidents': incidents
    })


# ----------------------------
# Create Incident
# ----------------------------
@login_required
def create_incident(request):
    if request.method == 'POST':
        form = IncidentForm(request.POST)
        if form.is_valid():
            incident = form.save()
            send_incident_notification(incident, request.user)
            return redirect('home')
    else:
        form = IncidentForm()

    return render(request, 'a_incidents/create_incident.html', {'form': form})


# ----------------------------
# Update Incident
# ----------------------------
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

    return render(request, 'a_incidents/incident_form.html', {'form': form})


# ----------------------------
# Delete Incident
# ----------------------------
@login_required
def delete_incident(request, pk):
    incident = get_object_or_404(Incident, pk=pk)

    if request.method == "POST":
        incident.delete()
        return redirect('home')

    return redirect('home')  # Optional fallback if someone tries GET


# ----------------------------
# Email Notification
# ----------------------------
def send_incident_notification(incident, created_by):
    # Hardcode emails for testing
    staff_emails = ['rehaan.rahman6@gmail.com']

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

Offender:
{incident.offender.name if incident.offender else 'N/A'}

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


# ----------------------------
# PDF Report Placeholder
# ----------------------------
@login_required
def incident_pdf_report(request, pk):
    incident = get_object_or_404(Incident, pk=pk)
    return render(request, 'a_incidents/incident_pdf.html', {'incident': incident})
