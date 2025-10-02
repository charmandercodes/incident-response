from django.test import TestCase
from a_incidents.models import Incident
from a_venues.models import Venue
from a_offenders.models import Offender

class IncidentModelTest(TestCase):
    def setUp(self):
        # Create a venue for the incident
        self.venue = Venue.objects.create(name="Test Venue")

        # Create an offender
        self.offender = Offender.objects.create(name="John Doe")

    def test_create_incident(self):
        # Create an incident with the minimum required fields
        incident = Incident.objects.create(
            title='Test Incident',
            description='This is a test incident',
            incident_type='other',
            venue=self.venue,
            offender=self.offender,
            warning='no',
            ban='no'
        )

        # Add the offender to the ManyToMany field
        incident.offenders.add(self.offender)

        # Assertions
        self.assertEqual(incident.title, 'Test Incident')
        self.assertEqual(incident.venue, self.venue)
        self.assertEqual(incident.offender, self.offender)
        self.assertIn(self.offender, incident.offenders.all())
        self.assertEqual(incident.warning, 'no')
        self.assertEqual(incident.ban, 'no')
