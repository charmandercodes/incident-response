from django.shortcuts import render
from django.db.models import Count
from django.db.models.functions import TruncDate
import json

from a_incidents.models import Incident
from a_offenders.models import Offender

def dashboard_view(request):
    # Get selected offender from request
    selected_offender_id = request.GET.get('offender', None)
    
    # Base queryset
    queryset = Incident.objects.filter(created_at__year__gte=2025)
    
    # Filter by offender if selected
    if selected_offender_id:
        queryset = queryset.filter(id=selected_offender_id)
    
    # Get incident counts by month
    incident_data = (
        queryset
        .annotate(date=TruncDate('created_at'))  # Changed from TruncMonth
        .values('date')
        .annotate(count=Count('id'))
        .order_by('date')
    )
    # Format data for Chart.js
    months = []
    counts = []
    
    for item in incident_data:
        months.append(item['date'].strftime('%b %d, %Y'))  # Changed format
        counts.append(item['count'])
    
    # Get all offenders for dropdown
    offenders = Offender.objects.all().order_by('name')
    
    context = {
        'chart_months': json.dumps(months),
        'chart_counts': json.dumps(counts),
        'offenders': offenders,
        'selected_offender_id': selected_offender_id,
    }
    
    return render(request, 'a_analytics/dashboard.html', context)