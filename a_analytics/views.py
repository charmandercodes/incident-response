from django.shortcuts import render
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.contrib import messages
import json

from a_incidents.models import Incident
from .filters import IncidentFilter


def dashboard_view(request):
    # Base queryset - incidents from 2025 onwards
    queryset = Incident.objects.filter(created_at__year__gte=2025)
    
    # Apply filter
    filterset = IncidentFilter(request.GET, queryset=queryset)
    
    # Check if filters are applied
    filters_applied = bool(request.GET.get('offender_name'))
    
    # Get the offender name for context
    offender_name = request.GET.get('offender_name', '')
    
    # Check for form errors
    if filterset.form.errors:
        for field, errors in filterset.form.errors.items():
            for error in errors:
                messages.error(request, error)
    
    # Get filtered queryset
    filtered_queryset = filterset.qs
    
    # Provide user feedback
    if offender_name and filtered_queryset.exists():
        # Get unique offenders in the results
        matching_offenders = filtered_queryset.values_list('offender__name', flat=True).distinct()
        offender_count = len(matching_offenders)
        
        if offender_count == 1:
            messages.success(request, f"Showing incidents for: {matching_offenders[0]}")
        else:
            offender_list = ", ".join(list(matching_offenders)[:3])
            if offender_count > 3:
                offender_list += f" and {offender_count - 3} more"
            messages.info(request, f"Found {offender_count} matching offenders: {offender_list}")
    elif offender_name and not filtered_queryset.exists():
        messages.warning(request, f"No offender found with name containing '{offender_name}'. Showing all incidents.")
        filtered_queryset = queryset  # Reset to show all
    
    # Get incident data for chart
    try:
        if not filtered_queryset.exists():
            messages.info(request, "No incidents have been recorded since 2025 yet.")
        
        incident_data = (
            filtered_queryset
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
        
        context = {
            'chart_months': json.dumps(months),
            'chart_counts': json.dumps(counts),
            'filter': filterset,
            'offender_name': offender_name,
            'filters_applied': filters_applied,
        }
        
    except Exception as e:
        messages.error(request, "An error occurred while loading incident data.")
        print(f"Dashboard error: {str(e)}")
        context = {
            'chart_months': json.dumps([]),
            'chart_counts': json.dumps([]),
            'filter': filterset,
            'offender_name': offender_name,
            'filters_applied': filters_applied,
        }
    
    return render(request, 'a_analytics/dashboard.html', context)