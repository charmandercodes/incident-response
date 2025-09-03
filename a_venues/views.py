from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Q
from .models import Venue
from django.contrib.auth.decorators import login_required
from .forms import VenueForm
# Create your views here.



def home_page(request):
    venues = Venue.objects.all().order_by('-created_at')
    
    # Handle search
    search_query = request.GET.get('search', '')
    if search_query:
        venues = venues.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(address__icontains=search_query) |
            Q(city__icontains=search_query) |
            Q(state__icontains=search_query) |
            Q(manager_name__icontains=search_query) |
            Q(venue_type__icontains=search_query)
        )
    
    # Regular request, return full page
    return render(request, 'a_venues/home.html', {
        'venues': venues
    })


@login_required
def create_venue(request):
    if request.method == 'POST':
        form = VenueForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')  # Redirect to a list or detail page
    else:
        form = VenueForm()

    return render(request, 'a_venues/create_venue.html', {'form': form})


@login_required
def delete_venue(request, pk):

    incident = get_object_or_404(Venue, pk=pk)

    if request.method == "POST":  # User confirmed deletion
        incident.delete()
        return redirect('venue-home')  # Go back to list after deleting


@login_required
def update_venue(request, pk):

    incident = get_object_or_404(Venue, pk=pk)

    if request.method == "POST":
        form = VenueForm(request.POST, instance=incident)
        if form.is_valid():
            form.save()
            return redirect('venue-home')
    else:
        form = VenueForm(instance=incident)


    return render(request, 'a_venues/update_venue.html', {'form': form})