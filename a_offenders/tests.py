from django.test import TestCase
from django.urls import reverse

class OffenderURLsTest(TestCase):
    def test_create_url_resolves(self):
        url = reverse("create-offender")
        self.assertEqual(url, "/offenders/create/")
        resp = self.client.get(url)
        self.assertIn(resp.status_code, (200, 302))  # 200 if public, 302 if login required

# Create your tests here.
