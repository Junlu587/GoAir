from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model

User = get_user_model()

class UserViewSetTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        # Create a test user with known credentials
        self.user_data = {
            "username": "testuser",
            "password": "testpassword"
        }
        self.user = User.objects.create_user(**self.user_data)

    def test_login_success(self):
        # The URL name depends on your router's basename. Here we assume it's "user".
        url = reverse('users-login')
        data = {
            "username": self.user_data['username'],
            "password": self.user_data['password']
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get("message"), "Login successfully")
        self.assertEqual(response.data.get("username"), self.user.username)

    def test_login_failure(self):
        url = reverse('users-login')
        data = {
            "username": self.user_data['username'],
            "password": "wrongpassword"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data.get("error"), "Invalid username or password")
