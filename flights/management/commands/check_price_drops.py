# flights/management/commands/check_price_drops.py
from django.core.management.base import BaseCommand
from flights.models import SavedTrip
from notifications.models import Notification
from external_api.book import BookAPI
from datetime import datetime


class Command(BaseCommand):
    help = "Check saved trips for price drops and notify users if price falls by 5% or more."

    def handle(self, *args, **options):
        api = BookAPI()
        saved_trips = SavedTrip.objects.all()
        for saved_trip in saved_trips:
            try:
                # Extract saved trip data (assumes keys: "price", "origin", "destination", "date", "airline", "flight_class")
                trip_data = saved_trip.trip_data
                saved_price = float(trip_data.get("price", {}).get("amount", 0))
                if saved_price == 0:
                    self.stdout.write(f"SavedTrip {saved_trip.id} has invalid price. Skipping.")
                    continue

                origin = trip_data.get("origin")
                destination = trip_data.get("destination")
                departure_date = trip_data.get("date")  # e.g., "2025-04-01"
                flight_class = trip_data.get("flight_class", "economy")
                airline = trip_data.get("airline", "")

                # For simplicity, assume oneway search and default sort
                trip_type = "oneway"
                sort = "BEST"
                return_date = ""

                # Re-fetch current flight info using BookAPI
                current_flights = api.search_flights(
                    origin=origin,
                    destination=destination,
                    trip_type=trip_type,
                    date=departure_date,
                    return_date=return_date,
                    flight_class=flight_class,
                    airline=airline,
                    sort=sort
                )

                # current_flights is expected to be a list of lists; choose the first flight if available.
                if current_flights and len(current_flights) > 0 and len(current_flights[0]) > 0:
                    current_info = current_flights[0][0]
                    current_price = float(current_info.get("price", {}).get("amount", 0))

                    # Calculate percentage drop
                    if current_price <= saved_price * 0.95:
                        message = (
                            f"Price drop alert! Your saved trip from {origin} to {destination} "
                            f"has dropped from {saved_price} to {current_price} "
                            f"{current_info.get('price', {}).get('currency', 'USD')}."
                        )
                        # Create a notification for the user
                        Notification.objects.create(user=saved_trip.user, message=message)
                        self.stdout.write(self.style.SUCCESS(
                            f"Notification created for user {saved_trip.user.username} for SavedTrip {saved_trip.id}."
                        ))
                else:
                    self.stdout.write(f"No current flight info found for SavedTrip {saved_trip.id}.")
            except Exception as e:
                self.stderr.write(f"Error processing SavedTrip {saved_trip.id}: {e}")
