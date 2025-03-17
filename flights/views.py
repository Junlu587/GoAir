from datetime import datetime
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from external_api.book import BookAPI
from flights.models import Flight
from .models import SavedTrip
from notifications.models import Notification
from flights.serializers import FlightSerializer
from decimal import Decimal
import json


@api_view(["POST"])
def search_flights(request):
    """
    Handles POST /api/flights/search/
    Expects JSON body with keys: origin, destination, departure_date, return_date, trip_type, flight_class, airline, sort
    """
    # Extract parameters
    origin = request.data.get("origin")
    destination = request.data.get("destination")
    departure_date = request.data.get("departure_date")
    return_date = request.data.get("return_date", "")
    trip_type = request.data.get("trip_type", "oneway")
    flight_class = request.data.get("flight_class", "economy")
    airline = request.data.get("airline", "")
    sort = request.data.get("sort", "BEST")

    # Validate required params
    if not origin or not destination or not departure_date:
        return Response({"error": "Missing required parameters: origin, destination, departure_date"}, status=400)

    # Instantiate BookAPI
    book_api = BookAPI()
    try:
        flight_results = book_api.search_flights(
            origin, destination, trip_type,
            departure_date, return_date,
            flight_class, airline, sort
        )

        if isinstance(flight_results, dict) and "error" in flight_results:
            return Response({"error": flight_results["error"]}, status=502)  # 502 Bad Gateway or 400-level

        if flight_results is None:
            return Response({"error": "No flights found or API error"}, status=500)

        # OPTIONAL: store flights in DB. flight_results is typically a list of lists.
        saved_flights = []
        for flight_list in flight_results:
            for f_info in flight_list:
                route = f_info.get("route", "Unknown-Unknown")
                origin_city, dest_city = route.split("-") if "-" in route else ("Unknown", "Unknown")
                date_str = f_info.get("date", "")
                times = f_info.get("time", {})
                departure_str = times.get("departure")
                arrival_str = times.get("arrival")
                price_data = f_info.get("price", {})
                amount = price_data.get("amount", 0)
                currency = price_data.get("currency", "USD")

                # Convert date/time if needed
                f_date = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else None
                d_time = datetime.strptime(departure_str, "%H:%M:%S").time() if departure_str else None
                a_time = datetime.strptime(arrival_str, "%H:%M:%S").time() if arrival_str else None

                # Example flight_number generator to avoid uniqueness conflicts
                gen_number = "API" + datetime.now().strftime("%H%M%S")

                # Create the Flight object
                flight_obj = Flight.objects.create(
                    airline=f_info.get("airline", "Unknown"),
                    flight_number=gen_number,
                    origin=origin_city,
                    destination=dest_city,
                    departure_date=f_date or datetime.now().date(),
                    departure_time=d_time,
                    arrival_date=f_date,  # if same-day arrival
                    arrival_time=a_time,
                    price=amount,
                    currency=currency,
                    aircraft=f_info.get("aircraft", "Unknown"),
                    # flight_token could be set here if BookAPI had a unique token
                )
                saved_flights.append(flight_obj.id)

        # Return the raw results + list of saved flight IDs
        return Response({
            "raw_api_data": flight_results,
            "saved_flight_ids": saved_flights
        }, status=200)

    except Exception as e:
        return Response({"error": str(e)}, status=500)

@api_view(["GET"])
def filter_and_sort_flights(request):
    """
    Endpoint to filter and sort saved Flight objects.
    Acceptable query parameters:
      - flight_class (e.g., "economy", "business")
      - airline (e.g., "UA")
      - sort: "price", "duration", or "departure_time"
    Example URL:
      /api/flights/filter/?flight_class=economy&airline=UA&sort=price
    """
    # Retrieve filter parameters from the query string
    flight_class = request.query_params.get("flight_class")
    airline = request.query_params.get("airline")
    sort_option = request.query_params.get("sort")

    # Start with all Flight objects
    qs = Flight.objects.all()

    # Apply filters if parameters are provided
    if flight_class:
        qs = qs.filter(flight_class__iexact=flight_class)
    if airline:
        qs = qs.filter(airline__iexact=airline)

    # Apply sorting
    if sort_option == "price":
        qs = qs.order_by("price")
    elif sort_option == "departure_time":
        # Order by departure_date first, then departure_time
        qs = qs.order_by("departure_date", "departure_time")
    elif sort_option == "duration":
        # Duration is a computed property. To sort by it, we'll convert the queryset to a list
        # and sort in Python. Note: Flights missing departure/arrival time will be sorted last.
        qs = list(qs)
        qs.sort(key=lambda f: f.duration if f.duration is not None else datetime.max - datetime.min)
    else:
        # Default ordering (if no sort is specified)
        qs = qs.order_by("departure_date", "departure_time")

    # Serialize the result
    serializer = FlightSerializer(qs, many=True)
    return Response(serializer.data)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def save_trip(request):
    """
    Save a flight trip to the user's profile.
    Expects a JSON payload with:
      - trip_data: The full flight search result (as JSON)
    Example request body:
      {
          "trip_data": {
              "date": "2025-04-01",
              "time": { "departure": "09:00:00", "arrival": "13:00:00" },
              "route": "Beijing-NewYork",
              "airline": "UA",
              "aircraft": "Boeing 747",
              "price": { "amount": 300, "currency": "USD" }
          }
      }
    """
    trip_data = request.data.get("trip_data")
    if not trip_data:
        return Response({"error": "Missing trip_data"}, status=400)

    # Create the SavedTrip object
    saved_trip = SavedTrip.objects.create(user=request.user, trip_data=trip_data)

    return Response({
        "message": "Trip saved successfully",
        "saved_trip_id": saved_trip.id
    }, status=200)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def check_saved_trips(request):
    """
    Manually check all saved trips for the authenticated user.
    For each saved trip, if the current flight price is at least 5% lower than the saved price,
    create a notification for the user.
    Returns a list of notifications created.
    """
    user = request.user
    saved_trips = SavedTrip.objects.filter(user=user)
    api = BookAPI()
    notifications_created = []

    for saved_trip in saved_trips:
        try:
            # Assume trip_data is stored as a JSON object with at least:
            # "price": {"amount": original_price, "currency": "USD"},
            # "origin", "destination", "date", "flight_class", "airline"
            trip_data = saved_trip.trip_data
            saved_price = Decimal(trip_data.get("price", {}).get("amount", 0))
            if saved_price == 0:
                continue

            origin = trip_data.get("origin")
            destination = trip_data.get("destination")
            departure_date = trip_data.get("date")  # e.g., "2025-04-01"
            flight_class = trip_data.get("flight_class", "economy")
            airline = trip_data.get("airline", "")

            # Call BookAPI to fetch current flight info
            # For simplicity, assume a oneway search with default sort
            current_flights = api.search_flights(
                origin=origin,
                destination=destination,
                trip_type="oneway",
                date=departure_date,
                return_date="",
                flight_class=flight_class,
                airline=airline,
                sort="BEST"
            )

            # current_flights is expected to be a list of lists; pick the first available flight if exists
            if current_flights and len(current_flights) > 0 and len(current_flights[0]) > 0:
                current_info = current_flights[0][0]
                current_price = Decimal(current_info.get("price", {}).get("amount", 0))

                # Check if current_price is at least 5% lower than saved_price
                if current_price <= saved_price * Decimal('0.95'):
                    message = (
                        f"Price drop alert: Your saved trip from {origin} to {destination} "
                        f"has dropped from {saved_price} to {current_price} "
                        f"{current_info.get('price', {}).get('currency', 'USD')}."
                    )
                    # Create a notification for the user
                    Notification.objects.create(user=user, message=message)
                    notifications_created.append(message)
            else:
                # You can log or ignore if no current flight data is found
                continue

        except Exception as e:
            # Log the error (you could also add error notifications here if desired)
            print(f"Error checking saved trip {saved_trip.id}: {e}")
            continue

    if notifications_created:
        return Response({"notifications": notifications_created}, status=200)
    else:
        return Response({"message": "No price drops detected at this time."}, status=200)