from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from notifications.models import Notification

User = get_user_model()


class NotificationViewSetTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.notification = Notification.objects.create(user=self.user, message='Test notification for view')

    def test_mark_as_read_action(self):
        # The URL name here depends on how your router is configured.
        # For example, if you registered the NotificationViewSet with basename 'notification',
        # the action URL name might be 'notification-mark-as-read'.
        url = reverse('notification-mark-as-read', kwargs={'pk': self.notification.pk})
        response = self.client.patch(url)
        self.notification.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.notification.is_read)
        self.assertEqual(response.data.get('status'), 'Notification marked as read')


from django.test import TestCase

# Create your tests here.
