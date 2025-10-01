# a_logs/tests.py
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.contrib.admin.models import LogEntry, ADDITION
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse


class LogsViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Create test users
        self.user1 = User.objects.create_user(username='admin', password='pass123')
        self.user2 = User.objects.create_user(username='testuser', password='pass123')
        
        # Get content type
        content_type = ContentType.objects.get_for_model(User)
        
        # Create test log entries
        LogEntry.objects.create(
            user=self.user1,
            content_type=content_type,
            object_id=self.user1.id,
            object_repr='admin',
            action_flag=ADDITION,
            change_message='Added user'
        )
        
        LogEntry.objects.create(
            user=self.user2,
            content_type=content_type,
            object_id=self.user2.id,
            object_repr='testuser',
            action_flag=ADDITION,
            change_message='Added user'
        )
    
    def test_exact_username_filter(self):
        """Test that exact username filtering works correctly and doesn't return partial matches"""
        # Search for 'admin' should only return logs from 'admin', not 'admin1'
        response = self.client.get(reverse('logs'), {'username': 'admin'})
        
        # Check response is successful
        self.assertEqual(response.status_code, 200)
        
        # Check that only exact matches are returned
        logs = response.context['logs']
        self.assertEqual(logs.count(), 1, "Should return exactly 1 log for 'admin'")
        
        # Verify it's the correct user
        self.assertEqual(logs.first().user.username, 'admin')
        
        # Verify filter is in context
        self.assertIn('filter', response.context)