from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Q
from .models import Offender
from django.contrib.auth.decorators import login_required
from .forms import OffenderForm

# Create your views here.
def offender_page(request):
    offenders = Offender.objects.all().order_by('-created_at')
    
    # Handle search
    search_query = request.GET.get('search', '')
    if search_query:
        offenders = offenders.filter(
            Q(name__icontains=search_query) |
            Q(contact_info__icontains=search_query)
        )
    
    # Regular request, return full page
    return render(request, 'a_offenders/home.html', {
        'offenders': offenders
    })

@login_required
def create_offender(request):
    if request.method == 'POST':
        form = OffenderForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('offender-home')  # Redirect to offender list page
    else:
        form = OffenderForm()
    
    return render(request, 'a_offenders/create_offender.html', {'form': form})

@login_required
def delete_offender(request, pk):
    offender = get_object_or_404(Offender, pk=pk)
    if request.method == "POST":  # User confirmed deletion
        offender.delete()
        return redirect('offender-home')  # Go back to list after deleting

@login_required
def update_offender(request, pk):
    offender = get_object_or_404(Offender, pk=pk)
    if request.method == "POST":
        form = OffenderForm(request.POST, instance=offender)
        if form.is_valid():
            form.save()
            return redirect('offender-home')
    else:
        form = OffenderForm(instance=offender)
    
    return render(request, 'a_offenders/update_offender.html', {'form': form})