# a_logs/tests.py
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse


class LogsViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
    
    def test_invalid_username_validation(self):
        """Test that invalid username is rejected and error message is shown"""
        # Test with username that's too short (less than 2 characters)
        response = self.client.get(reverse('logs'), {'username': 'a'})
        
        # Check response is successful
        self.assertEqual(response.status_code, 200)
        
        # Check that error message appears
        messages = list(response.context['messages'])
        self.assertTrue(
            any('at least 2 characters' in str(m) for m in messages),
            "Expected validation error message for short username"
        )
        
        # Verify form is in context
        self.assertIn('form', response.context)