from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import patch
from datetime import datetime
from django.contrib.auth import get_user_model
from flights.models import Flight, SavedTrip

User = get_user_model()

class FlightIntegrationTest(APITestCase):
    def setUp(self):
        # Create and authenticate a test user
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.client.force_authenticate(user=self.user)

    @patch('flights.views.BookAPI.search_flights')
    def test_flight_search_and_save_trip_integration(self, mock_search_flights):
        # Define sample flight search data as returned by BookAPI.
        sample_flight_data = [
            [
                {
                    "route": "NYC-JFK",
                    "date": "2025-04-01",
                    "time": {"departure": "09:00:00", "arrival": "11:00:00"},
                    "price": {"amount": 150, "currency": "USD"},
                    "airline": "Delta",
                    "aircraft": "Boeing 737"
                }
            ]
        ]
        # Set the mock to return the sample flight data.
        mock_search_flights.return_value = sample_flight_data

        # --- Step 1: Flight Search ---
        flight_search_url = '/api/flights/search/'
        search_payload = {
            "origin": "NYC",
            "destination": "JFK",
            "departure_date": "2025-04-01",
            "return_date": "",
            "trip_type": "oneway",
            "flight_class": "economy",
            "airline": "",
            "sort": "BEST"
        }
        search_response = self.client.post(flight_search_url, search_payload, format='json')
        self.assertEqual(search_response.status_code, status.HTTP_200_OK)
        # Verify that a Flight object has been created.
        self.assertEqual(Flight.objects.count(), 1)
        flight_obj = Flight.objects.first()
        self.assertEqual(flight_obj.airline, "Delta")
        self.assertEqual(flight_obj.origin, "NYC")
        self.assertEqual(flight_obj.destination, "JFK")
        self.assertEqual(flight_obj.departure_date, datetime.strptime("2025-04-01", "%Y-%m-%d").date())

        # --- Step 2: Save Trip ---
        # After the flight search step, retrieve the created flight.
        flight_obj = Flight.objects.first()

        # Build a sample trip payload using flight data.
        save_trip_url = '/api/flights/save_trip/'
        sample_trip_data = {
            "date": "2025-04-01",
            "time": {"departure": "09:00:00", "arrival": "11:00:00"},
            "route": "NYC-JFK",
            "airline": "Delta",
            "aircraft": "Boeing 737",
            "price": {"amount": 150, "currency": "USD"},
            # Additional fields required by the backend logic.
            "origin": "NYC",
            "destination": "JFK",
            "flight_class": "economy",
            "flight_id": flight_obj.id  # Added flight reference
        }
        trip_payload = {"trip_data": sample_trip_data}
        save_response = self.client.post(save_trip_url, trip_payload, format='json')
        self.assertEqual(save_response.status_code, status.HTTP_200_OK)
        self.assertIn("message", save_response.data)
        self.assertEqual(save_response.data.get("message"), "Trip saved successfully")
        self.assertIn("saved_trip_id", save_response.data)
        # Verify that the SavedTrip object is created.
        self.assertEqual(SavedTrip.objects.count(), 1)

    def test_filter_and_sort_flights_integration(self):
        # --- Precondition: Create a Flight object manually ---
        Flight.objects.create(
            airline="Delta",
            flight_number="API123456",
            origin="NYC",
            destination="JFK",
            departure_date=datetime.strptime("2025-04-01", "%Y-%m-%d").date(),
            departure_time=datetime.strptime("09:00:00", "%H:%M:%S").time(),
            arrival_date=datetime.strptime("2025-04-01", "%Y-%m-%d").date(),
            arrival_time=datetime.strptime("11:00:00", "%H:%M:%S").time(),
            price=150,
            currency="USD",
            aircraft="Boeing 737",
            flight_class="economy"
        )

        # --- Step 3: Flight Filtering ---
        filter_url = '/api/flights/filter/'
        filter_params = {
            "flight_class": "economy",
            "airline": "Delta",
            "sort": "price"
        }
        filter_response = self.client.get(filter_url, filter_params)
        self.assertEqual(filter_response.status_code, status.HTTP_200_OK)
        # Ensure at least one flight is returned.
        self.assertGreaterEqual(len(filter_response.data), 1)
