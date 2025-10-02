from django.shortcuts import render
from django.contrib.admin.models import LogEntry
from django.contrib import messages
from .filters import LogEntryFilter


def logs_view(request):
    # Apply filters
    queryset = LogEntry.objects.select_related('user', 'content_type').all()
    filterset = LogEntryFilter(request.GET, queryset=queryset)
    
    # Check if filters are applied
    filters_applied = any(request.GET.values())
    
    # Get filtered logs (limit to 100)
    logs = filterset.qs.order_by('-action_time')[:100]
    
    # Provide feedback
    if logs.count() == 0 and filters_applied:
        messages.warning(request, "No logs match your filter criteria.")
    elif logs.count() == 100:
        messages.info(request, "Showing the latest 100 logs. Use filters to narrow results.")
    
    context = {
        'filter': filterset,  # Note: it's 'filter', not 'form'
        'logs': logs,
        'filters_applied': filters_applied,
    }
    
    return render(request, 'a_logs/page.html', context)