from django.test import TestCase
from django.test import TestCase
from a_offenders.models import Offender

class OffenderModelTest(TestCase):
    def test_str_returns_name(self):
        o = Offender.objects.create(name="Jane Doe")
        self.assertEqual(str(o), "Jane Doe")

# Create your tests here.
