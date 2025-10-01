from django.shortcuts import render
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.contrib import messages
import json

from a_incidents.models import Incident
from a_offenders.models import Offender
from .forms import OffenderFilterForm

def dashboard_view(request):
    form = OffenderFilterForm(request.GET)
    offender_name = ''
    
    # Initialize context
    context = {
        'chart_months': json.dumps([]),
        'chart_counts': json.dumps([]),
        'form': form,
    }
    
    # Base queryset
    queryset = Incident.objects.filter(created_at__year__gte=2025)
    
    # Validate form
    if form.is_valid():
        offender_name = form.cleaned_data.get('offender_name', '')
        
        if offender_name:
            try:
                matching_offenders = Offender.objects.filter(name__icontains=offender_name)
                
                if not matching_offenders.exists():
                    messages.warning(request, f"No offender found with name containing '{offender_name}'. Showing all incidents.")
                else:
                    queryset = queryset.filter(offender__in=matching_offenders)
                    
                    if matching_offenders.count() == 1:
                        messages.success(request, f"Showing incidents for: {matching_offenders.first().name}")
                    else:
                        offender_names = ", ".join([o.name for o in matching_offenders[:3]])
                        if matching_offenders.count() > 3:
                            offender_names += f" and {matching_offenders.count() - 3} more"
                        messages.info(request, f"Found {matching_offenders.count()} matching offenders: {offender_names}")
                        
            except Exception as e:
                messages.error(request, "An error occurred while searching for the offender.")
                print(f"Error: {str(e)}")
    else:
        # Form is invalid, display errors
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, error)
    
    # Get incident data
    try:
        if not queryset.exists():
            if offender_name:
                messages.warning(request, "No incidents found for the selected offender since 2025.")
            else:
                messages.info(request, "No incidents have been recorded since 2025 yet.")
        
        incident_data = (
            queryset
            .annotate(date=TruncDate('created_at'))
            .values('date')
            .annotate(count=Count('id'))
            .order_by('date')
        )
        
        months = []
        counts = []
        
        for item in incident_data:
            if item['date']:
                months.append(item['date'].strftime('%b %d, %Y'))
                counts.append(item['count'])
        
        context['chart_months'] = json.dumps(months)
        context['chart_counts'] = json.dumps(counts)
        
    except Exception as e:
        messages.error(request, "An error occurred while loading incident data.")
        print(f"Dashboard error: {str(e)}")
    
    return render(request, 'a_analytics/dashboard.html', context)