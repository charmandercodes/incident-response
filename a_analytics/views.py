from django.shortcuts import render

# Create your views here.
# views.py
from django.shortcuts import render
from django.db.models import Count
from django.db.models.functions import TruncMonth
import json

from a_incidents.models import Incident

def dashboard_view(request):
    # Get incident counts by month since 2025
    incident_data = (
        Incident.objects
        .filter(created_at__year__gte=2025)
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )
    
    # Format data for Chart.js
    months = []
    counts = []
    
    for item in incident_data:
        months.append(item['month'].strftime('%B %Y'))
        counts.append(item['count'])
    
    context = {
        'chart_months': json.dumps(months),
        'chart_counts': json.dumps(counts),
    }
    
    return render(request, 'a_analytics/dashboard.html', context)