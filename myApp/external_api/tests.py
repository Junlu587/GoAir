from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import patch
from django.contrib.auth import get_user_model

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GoAir.settings')
import django
django.setup()

User = get_user_model()

class ExternalAPITest(APITestCase):
    def setUp(self):
        # Create and authenticate a test user
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.client.force_authenticate(user=self.user)

    @patch('external_api.views.BookAPI.search_flights')
    def test_flight_search(self, mock_search_flights):
        # Prepare a sample response from the mocked search_flights method.
        sample_flight_data = {
            "flights": [
                {"route": "NYC-JFK", "date": "2025-04-01", "airline": "Delta"}
            ]
        }
        mock_search_flights.return_value = sample_flight_data

        # Build the query parameters as expected by the endpoint.
        params = {
            "origin": "NYC",
            "destination": "JFK",
            "type": "oneway",
            "date": "2025-04-01",
            "return_date": "",
            "flight_class": "economy",
            "airline": "",
            "sort": "BEST"
        }
        # Assuming the URL is /api/external/flight-search/
        url = '/api/external/flight-search/'
        response = self.client.get(url, params)

        # Verify that the endpoint returns HTTP 200 and the mocked data.
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, sample_flight_data)

    @patch('external_api.views.BookAPI.search_destination')
    def test_airport_search(self, mock_search_destination):
        # Prepare a sample response from the mocked search_destination method.
        sample_airport_data = {"data": "sample_destination_data"}
        mock_search_destination.return_value = sample_airport_data

        params = {"query": "LAX"}
        # Assuming the URL is /api/external/airport-search/
        url = '/api/external/airport-search/'
        response = self.client.get(url, params)

        # Verify that the endpoint returns HTTP 200 and the mocked data.
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, sample_airport_data)
