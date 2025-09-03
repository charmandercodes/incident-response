from django.shortcuts import render, redirect
from a_incidents.models import Incident
from .forms import IncidentForm

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

def create_incident(request):
    if request.method == 'POST':
        form = IncidentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')  # Redirect to a list or detail page
    else:
        form = IncidentForm()

    return render(request, 'a_incidents/create_incident.html', {'form': form})



# views.py
from django.shortcuts import get_object_or_404, redirect, render
from .models import Incident

def delete_incident(request, pk):

    incident = get_object_or_404(Incident, pk=pk)

    if request.method == "POST":  # User confirmed deletion
        incident.delete()
        return redirect('home')  # Go back to list after deleting

    # Show confirmation page
    return render(request, 'a_incidents/confirm_delete.html', {'incident': incident})


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