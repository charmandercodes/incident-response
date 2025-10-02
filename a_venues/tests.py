from django.test import TestCase
from a_venues.models import Venue

class VenueModelTest(TestCase):
    def test_create_venue(self):
        # Create a simple venue
        venue = Venue.objects.create(
            name="Test Venue",
            description="A simple test venue",
            address="123 Test Street",
            city="Test City",
            state="TS",
            postal_code="12345"
        )

        # Assertions to check that the object was created correctly
        self.assertEqual(venue.name, "Test Venue")
        self.assertEqual(venue.city, "Test City")
        self.assertTrue(venue.is_active)
