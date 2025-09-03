from django.shortcuts import render
from django.contrib.admin.models import LogEntry


def logs_view(request):
    logs = LogEntry.objects.all().order_by('-action_time')[:100]  # Get latest 100 logs
    return render(request, 'a_logs/page.html', {'logs': logs})