import csv
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Q, Count
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from .models import Offender
from .forms import OffenderForm
from datetime import timedelta
from django.utils import timezone
from .models import Offender, Warning, Ban


def offender_page(request):
    offenders = Offender.objects.all().order_by('-created_at')

    # search
    q = request.GET.get('search', '').strip()
    if q:
        offenders = offenders.filter(
            Q(name__icontains=q) |
            Q(contact_info__icontains=q) |
            Q(notes__icontains=q)
        )

    return render(request, 'a_offenders/home.html', {
        'offenders': offenders
    })


@staff_member_required
def offenders_csv(request):
    """
    Export offenders with counts as CSV (staff only).
    """
    resp = HttpResponse(content_type="text/csv")
    resp["Content-Disposition"] = 'attachment; filename="offenders.csv"'
    writer = csv.writer(resp)
    writer.writerow(["Name", "Warnings", "Active bans"])

    for o in Offender.objects.annotate(warn_count=Count("warnings")):
        writer.writerow([o.name, o.warn_count, "Yes" if o.is_currently_banned else "No"])

    return resp


@login_required
def create_offender(request):
    if request.method == 'POST':
        form = OffenderForm(request.POST, request.FILES)   # <-- include request.FILES
        if form.is_valid():
            offender = form.save()

            # Optional quick Warning
            if form.cleaned_data.get("warning_now"):
                Warning.objects.create(
                    offender=offender,
                    severity=(form.cleaned_data.get("warning_severity") or "M"),
                    notes="Auto-created at offender creation.",
                    venue="",  # fill if you have venue context
                    created_by=request.user,
                )

            # Optional quick Ban
            if form.cleaned_data.get("ban_now"):
                start = timezone.localdate()
                dur = form.cleaned_data.get("ban_duration") or ""
                end = None if dur in ("", "permanent") else start + timedelta(days=int(dur))

                Ban.objects.create(
                    offender=offender,
                    reason=form.cleaned_data.get("ban_reason") or "Auto-created at offender creation.",
                    venue="",  # fill if needed
                    start_date=start,
                    end_date=end,
                    issued_by=request.user,
                )

            return redirect('offender-home')
    else:
        form = OffenderForm()

    return render(request, 'a_offenders/create_offender.html', {'form': form})


@login_required
def update_offender(request, pk):
    offender = get_object_or_404(Offender, pk=pk)
    if request.method == "POST":
        form = OffenderForm(request.POST, request.FILES, instance=offender)  # <-- include request.FILES
        if form.is_valid():
            offender = form.save()

            # (Optionally allow quick actions on update too)
            if form.cleaned_data.get("warning_now"):
                Warning.objects.create(
                    offender=offender,
                    severity=(form.cleaned_data.get("warning_severity") or "M"),
                    notes="Auto-created during offender update.",
                    venue="",
                    created_by=request.user,
                )

            if form.cleaned_data.get("ban_now"):
                start = timezone.localdate()
                dur = form.cleaned_data.get("ban_duration") or ""
                end = None if dur in ("", "permanent") else start + timedelta(days=int(dur))
                Ban.objects.create(
                    offender=offender,
                    reason=form.cleaned_data.get("ban_reason") or "Auto-created during offender update.",
                    venue="",
                    start_date=start,
                    end_date=end,
                    issued_by=request.user,
                )

            return redirect('offender-home')
    else:
        form = OffenderForm(instance=offender)

    return render(request, 'a_offenders/update_offender.html', {'form': form, 'offender': offender})


@login_required
def delete_offender(request, pk):
    offender = get_object_or_404(Offender, pk=pk)
    if request.method == "POST":
        offender.delete()
        return redirect('offender-home')
    # if someone hits this via GET, just go back to the list
    return redirect('offender-home')
