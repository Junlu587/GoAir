from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import patch
from datetime import datetime
from flights.models import Flight
from django.contrib.auth import get_user_model


User = get_user_model()

class FlightSearchTest(APITestCase):
    def setUp(self):
        # Create and authenticate a test user
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.client.force_authenticate(user=self.user)

    @patch('external_api.book.BookAPI.search_flights')
    def test_search_flights_success(self, mock_search_flights):
        # Sample response that the BookAPI should return.
        sample_api_response = [
            [
                {
                    "route": "NYC-JFK",
                    "date": "2025-04-01",
                    "time": {"departure": "09:00:00", "arrival": "11:00:00"},
                    "price": {"amount": 100, "currency": "USD"},
                    "airline": "Delta",
                    "aircraft": "Boeing 737"
                }
            ]
        ]
        # Set the mock to return our sample response.
        mock_search_flights.return_value = sample_api_response

        # Prepare POST data as expected by the search_flights endpoint.
        post_data = {
            "origin": "NYC",
            "destination": "JFK",
            "departure_date": "2025-04-01",
            "return_date": "",
            "trip_type": "oneway",
            "flight_class": "economy",
            "airline": "",
            "sort": "BEST"
        }

        # If you have a URL name set for the search_flights endpoint, you can reverse it.
        # Otherwise, you can directly use the URL path.
        # For example, if the URL name is 'search_flights':
        # url = reverse('search_flights')
        url = '/api/flights/search/'  # Adjust if needed

        response = self.client.post(url, post_data, format='json')

        # Check for a successful response.
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("raw_api_data", response.data)
        self.assertIn("saved_flight_ids", response.data)

        # Verify that one Flight object has been created.
        self.assertEqual(Flight.objects.count(), 1)
        flight = Flight.objects.first()
        self.assertEqual(flight.airline, "Delta")
        self.assertEqual(flight.origin, "NYC")
        self.assertEqual(flight.destination, "JFK")
        # Check if the departure_date is parsed correctly.
        self.assertEqual(flight.departure_date, datetime.strptime("2025-04-01", "%Y-%m-%d").date())
