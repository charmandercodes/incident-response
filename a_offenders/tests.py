# a_offenders/tests/test_bans_and_notifications.py
import datetime
from unittest.mock import patch
from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from a_offenders.models import Offender, Ban
from a_venues.models import Venue
from a_notifications.models import NotificationLog
from a_notifications import utils as notif

User = get_user_model()

class BanReadModelTests(TestCase):
    def setUp(self):
        self.offender = Offender.objects.create(name="John Doe")

    def test_days_remaining_and_active(self):
        today = timezone.localdate()
        ban_perm = Ban.objects.create(offender=self.offender, reason="Test", start_date=today, end_date=None)
        self.assertTrue(ban_perm.is_active)
        self.assertIsNone(ban_perm.days_remaining)

        ban_future = Ban.objects.create(offender=self.offender, reason="Test", start_date=today, end_date=today + datetime.timedelta(days=5))
        self.assertTrue(ban_future.is_active)
        self.assertEqual(ban_future.days_remaining, 5)

        ban_past = Ban.objects.create(offender=self.offender, reason="Test", start_date=today - datetime.timedelta(days=10), end_date=today - datetime.timedelta(days=1))
        self.assertFalse(ban_past.is_active)
        self.assertEqual(ban_past.days_remaining, 0)

class VenueNotificationTests(TestCase):
    @patch("a_notifications.utils.send_mail")
    def test_send_venue_ban_success(self, mock_send):
        admin = User.objects.create(username="admin")
        off = Offender.objects.create(name="Jane O")
        venue = Venue.objects.create(name="Mall A", address="x", city="c", state="s", postal_code="0000", email="v@mall.com")
        today = timezone.localdate()
        ban = Ban.objects.create(offender=off, reason="Reason", start_date=today, end_date=today + datetime.timedelta(days=7), issued_by=admin)
        # annotate venue on ban if you added FK; otherwise pass venue via service signature adjustment
        ban.venue_obj = venue  # only if you added this dynamic attr for the demo
        notif.send_venue_ban(ban)
        self.assertTrue(NotificationLog.objects.filter(ban=ban, type="VENUE_BAN_ISSUED", status="SENT").exists())
        self.assertTrue(mock_send.called)

    def test_send_venue_ban_missing_email(self):
        admin = User.objects.create(username="admin")
        off = Offender.objects.create(name="Jane O")
        venue = Venue.objects.create(name="Mall B", address="x", city="c", state="s", postal_code="0000", email="")
        today = timezone.localdate()
        ban = Ban.objects.create(offender=off, reason="Reason", start_date=today, end_date=today + datetime.timedelta(days=7), issued_by=admin)
        ban.venue_obj = venue
        notif.send_venue_ban(ban)
        log = NotificationLog.objects.get(ban=ban, type="VENUE_BAN_ISSUED")
        self.assertEqual(log.status, "FAILED")
        self.assertIn("missing_email", (log.error or ""))

class ExpiryCommandTests(TestCase):
    @patch("a_notifications.utils.send_mail")
    def test_scan_expiring_t3_and_t0(self, _):
        off = Offender.objects.create(name="Alex P")
        today = timezone.localdate()
        ban_t3 = Ban.objects.create(offender=off, reason="R", start_date=today, end_date=today + datetime.timedelta(days=3))
        ban_t0 = Ban.objects.create(offender=off, reason="R", start_date=today - datetime.timedelta(days=7), end_date=today)

        from django.core import management
        management.call_command("scan_expiring_bans")

        self.assertTrue(NotificationLog.objects.filter(ban=ban_t3, type="BAN_EXPIRY_T3").exists())
        self.assertTrue(NotificationLog.objects.filter(ban=ban_t0, type="BAN_EXPIRY_T0").exists())

        # idempotent
        management.call_command("scan_expiring_bans")
        self.assertEqual(NotificationLog.objects.filter(ban=ban_t3, type="BAN_EXPIRY_T3").count(), 1)


# Create your tests here.
