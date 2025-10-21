from django.core.management.base import BaseCommand # pyright: ignore[reportMissingModuleSource]
from django.utils import timezone
from datetime import timedelta
from a_offenders.models import Ban
from a_notifications.utils import send_expiry_alert
from a_notifications.models import NotificationLog

class Command(BaseCommand):
    help = "Send T-3 and T-0 ban expiry alerts (idempotent)."

    def handle(self, *args, **kwargs):
        today = timezone.localdate()
        t3 = today + timedelta(days=3)

        # T-3
        for ban in Ban.objects.filter(end_date=t3):
            # idempotency: skip if a log for this ban+type exists today
            if NotificationLog.objects.filter(ban=ban, type='BAN_EXPIRY_T3', created_at__date=today).exists():
                continue
            send_expiry_alert(ban, 'T-3')

        # T-0
        for ban in Ban.objects.filter(end_date=today):
            if NotificationLog.objects.filter(ban=ban, type='BAN_EXPIRY_T0', created_at__date=today).exists():
                continue
            send_expiry_alert(ban, 'T-0')
