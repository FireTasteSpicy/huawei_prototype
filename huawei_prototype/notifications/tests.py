from django.test import TestCase, Client
from django.urls import reverse
from dashboard.models import Notification, User
from datetime import datetime, timedelta

class NotificationModelTests(TestCase):
    """Tests for the Notification model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create(
            username="testuser",
            password="password123",
            email="test@example.com"
        )
        
        self.notification = Notification.objects.create(
            message="Test notification message",
            category="alert",
            read_status=False,
            user=self.user
        )
    
    def test_notification_creation(self):
        """Test basic notification creation and attributes."""
        self.assertEqual(self.notification.message, "Test notification message")
        self.assertEqual(self.notification.category, "alert")
        self.assertFalse(self.notification.read_status)
        self.assertEqual(self.notification.user, self.user)
        
    def test_notification_string_representation(self):
        """Test the string representation of a notification."""
        expected_string = f"alert: Test notification message..."
        self.assertEqual(str(self.notification), expected_string)


class NotificationViewTests(TestCase):
    """Tests for the notification view functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.notifications_url = reverse('notifications')
        
        # Create a test user
        self.user = User.objects.create(
            username="testuser",
            password="password123",
            email="test@example.com"
        )
        
        # Create test notifications with different statuses
        self.notification1 = Notification.objects.create(
            message="Unread alert notification",
            category="alert",
            read_status=False,
            user=self.user
        )
        
        self.notification2 = Notification.objects.create(
            message="Read message notification",
            category="message",
            read_status=True,
            user=self.user
        )
        
        self.notification3 = Notification.objects.create(
            message="Unread threshold notification",
            category="threshold_triggered",
            read_status=False,
            user=self.user
        )
    
    def test_notifications_view_loads(self):
        """Test that the notifications view loads successfully."""
        response = self.client.get(self.notifications_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'notifications/notifications.html')
        
    def test_notifications_list_all(self):
        """Test that all notifications are listed by default."""
        response = self.client.get(self.notifications_url)
        self.assertEqual(len(response.context['notifications']), 3)
        
    def test_notifications_filter_unread(self):
        """Test filtering notifications by unread status."""
        response = self.client.get(f"{self.notifications_url}?status=unread")
        self.assertEqual(len(response.context['notifications']), 2)
        for notification in response.context['notifications']:
            self.assertFalse(notification.read_status)
        
    def test_notifications_filter_read(self):
        """Test filtering notifications by read status."""
        response = self.client.get(f"{self.notifications_url}?status=read")
        self.assertEqual(len(response.context['notifications']), 1)
        for notification in response.context['notifications']:
            self.assertTrue(notification.read_status)
            
    def test_mark_notification_as_read(self):
        """Test marking a notification as read."""
        # Ensure notification1 is unread initially
        self.assertFalse(self.notification1.read_status)
        
        # Mark as read
        response = self.client.get(f"{self.notifications_url}?mark_read={self.notification1.notification_id}")
        
        # Check response and reload the notification from the database
        self.assertEqual(response.status_code, 200)
        self.notification1.refresh_from_db()
        self.assertTrue(self.notification1.read_status)
        
    def test_mark_notification_as_unread(self):
        """Test marking a notification as unread."""
        # Ensure notification2 is read initially
        self.assertTrue(self.notification2.read_status)
        
        # Mark as unread
        response = self.client.get(f"{self.notifications_url}?mark_unread={self.notification2.notification_id}")
        
        # Check response and reload the notification from the database
        self.assertEqual(response.status_code, 200)
        self.notification2.refresh_from_db()
        self.assertFalse(self.notification2.read_status)
        
    def test_invalid_notification_id(self):
        """Test handling of invalid notification IDs."""
        # Try to mark a non-existent notification as read
        response = self.client.get(f"{self.notifications_url}?mark_read=9999")
        self.assertEqual(response.status_code, 200)  # Should not cause error, just log it
        
        # Try with non-numeric ID
        response = self.client.get(f"{self.notifications_url}?mark_read=abc")
        self.assertEqual(response.status_code, 200)  # Should not cause error, just log it


class NotificationPaginationTests(TestCase):
    """Tests for notification pagination."""
    
    def setUp(self):
        """Set up test data with many notifications."""
        self.client = Client()
        self.notifications_url = reverse('notifications')
        
        # Create a test user
        self.user = User.objects.create(
            username="testuser",
            password="password123",
            email="test@example.com"
        )
        
        # Create 15 test notifications (to test pagination)
        for i in range(15):
            Notification.objects.create(
                message=f"Test notification {i+1}",
                category="message",
                read_status=(i % 2 == 0),  # Alternate read/unread
                user=self.user
            )
    
    def test_pagination_exists(self):
        """Test that pagination is present when there are many notifications."""
        response = self.client.get(self.notifications_url)
        self.assertTrue('notifications' in response.context)
        self.assertTrue(response.context['notifications'].has_other_pages())
        
    def test_first_page_has_correct_number(self):
        """Test that the first page has the correct number of notifications."""
        response = self.client.get(self.notifications_url)
        self.assertEqual(len(response.context['notifications']), 10)  # 10 per page
        
    def test_second_page_has_remaining(self):
        """Test that the second page has the remaining notifications."""
        response = self.client.get(f"{self.notifications_url}?page=2")
        self.assertEqual(len(response.context['notifications']), 5)  # 5 remaining
        
    def test_filters_maintain_with_pagination(self):
        """Test that filters are maintained during pagination."""
        response = self.client.get(f"{self.notifications_url}?status=read&page=1")
        
        # Count total read notifications (should be about half of 15 = ~7-8)
        read_count = Notification.objects.filter(read_status=True).count()
        
        # First page should have either all read notifications or maximum page size
        expected_count = min(read_count, 10)
        self.assertEqual(len(response.context['notifications']), expected_count)
        
        # All notifications should be read
        for notification in response.context['notifications']:
            self.assertTrue(notification.read_status)

