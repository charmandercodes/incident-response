from django.shortcuts import render
from django.contrib.admin.models import LogEntry
from django.contrib import messages
from django.db.models import Q
from datetime import datetime, time

from .forms import LogFilterForm


def logs_view(request):
    form = LogFilterForm(request.GET)
    
    # Base queryset
    logs = LogEntry.objects.select_related('user', 'content_type').all()
    
    # Track if any filters are applied
    filters_applied = False
    
    # Validate and apply filters
    if form.is_valid():
        username = form.cleaned_data.get('username')
        action_flag = form.cleaned_data.get('action_flag')
        date_from = form.cleaned_data.get('date_from')
        date_to = form.cleaned_data.get('date_to')
        
        # Filter by username
        if username:
            filters_applied = True
            matching_logs = logs.filter(user__username__icontains=username)
            
            if not matching_logs.exists():
                messages.warning(request, f"No logs found for user containing '{username}'. Showing all logs.")
            else:
                logs = matching_logs
                messages.success(request, f"Filtered logs by user: {username}")
        
        # Filter by action type
        if action_flag:
            filters_applied = True
            logs = logs.filter(action_flag=action_flag)
            action_name = dict(form.fields['action_flag'].choices).get(action_flag)
            messages.info(request, f"Showing only '{action_name}' actions")
        
        # Filter by date range
        if date_from:
            filters_applied = True
            # Combine date with start of day (00:00:00)
            datetime_from = datetime.combine(date_from, time.min)
            logs = logs.filter(action_time__gte=datetime_from)
            messages.info(request, f"Showing logs from {date_from.strftime('%Y-%m-%d')} onwards")
        
        if date_to:
            filters_applied = True
            # Combine date with end of day (23:59:59)
            datetime_to = datetime.combine(date_to, time.max)
            logs = logs.filter(action_time__lte=datetime_to)
            messages.info(request, f"Showing logs up to {date_to.strftime('%Y-%m-%d')}")
        
    else:
        # Form has validation errors
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, error)
    
    # Order and limit results
    logs = logs.order_by('-action_time')[:100]
    
    # Show info about result count
    log_count = logs.count()
    if log_count == 0:
        if filters_applied:
            messages.warning(request, "No logs match your filter criteria.")
        else:
            messages.info(request, "No logs found in the system.")
    elif log_count == 100:
        messages.info(request, "Showing the latest 100 logs. Use filters to narrow results.")
    
    context = {
        'logs': logs,
        'form': form,
        'filters_applied': filters_applied,
    }
    
    return render(request, 'a_logs/page.html', context)