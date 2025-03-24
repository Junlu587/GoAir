from datetime import datetime
from decimal import Decimal
import json

from django.core.paginator import Paginator
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from myApp.external_api.book import BookAPI
from myApp.flights.models import Flight
from myApp.flights.serializers import FlightSerializer
from .models import SavedTrip
from myApp.notifications.models import Notification
import re
from decimal import Decimal


@csrf_exempt
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def search_flights(request):
    # Debug print to confirm the view is being called
    print("search_flights called, method:", request.method)
    print("Request data:", request.data)

    # Disable CSRF enforcement explicitly
    request._dont_enforce_csrf_checks = True

    if request.method == 'POST':
        origin = request.data.get("origin")
        destination = request.data.get("destination")
        departure_date = request.data.get("departure_date")
        return_date = request.data.get("return_date", "")
        trip_type = request.data.get("trip_type", "oneway")
        flight_class = request.data.get("flight_class", "economy")
        airline = request.data.get("airline", "")
        sort = request.data.get("sort", "BEST")

        if not origin or not destination or not departure_date:
            return Response({"error": "Missing required parameters: origin, destination, departure_date"}, status=400)

        book_api = BookAPI()
        try:
            flight_results = book_api.search_flights(
                origin, destination, trip_type,
                departure_date, return_date,
                flight_class, airline, sort
            )

            # Print the flight_results structure for debugging
            print("API response structure:", type(flight_results))

            # Handle empty results
            if not flight_results or len(flight_results) == 0:
                return Response({
                    "results": [],
                    "message": "No flights found for this route and date"
                }, status=200)

            # Flatten flight_results if it's a list of lists
            flattened = []
            for flist in flight_results:
                if isinstance(flist, list):
                    flattened.extend(flist)
                else:
                    flattened.append(flist)

            # Add deduplication step:
            # Remove duplicate flights
            flattened = remove_duplicate_flights(flattened)
            print(f"After deduplication: {len(flattened)} unique flights")

            # Optional: store flights in DB (with unique flight numbers)
            saved_flights = []
            timestamp = datetime.now().strftime('%H%M%S')

            try:
                for idx, f_info in enumerate(flattened):
                    route = f_info.get("route", "Unknown-Unknown")
                    origin_city, dest_city = route.split("-") if "-" in route else ("Unknown", "Unknown")

                    date_str = f_info.get("date", "")
                    times = f_info.get("time", {})
                    departure_str = times.get("departure")
                    arrival_str = times.get("arrival")
                    price_data = f_info.get("price", {})
                    amount = price_data.get("amount", 0)
                    currency = price_data.get("currency", "USD")

                    f_date = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else None
                    d_time = datetime.strptime(departure_str, "%H:%M:%S").time() if departure_str else None
                    a_time = datetime.strptime(arrival_str, "%H:%M:%S").time() if arrival_str else None

                    # Create a TRULY unique flight number with timestamp and index
                    gen_number = f"F{timestamp[-4:]}{idx:02d}"

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
                    )
                    saved_flights.append(flight_obj.id)
            except Exception as db_error:
                # Log DB error but continue with returning API results
                print(f"Error saving flights to database: {str(db_error)}")

            # Apply pagination (6 results per page)
            page_number = request.query_params.get("page") or request.data.get("page") or 1
            paginator = Paginator(flattened, 20)
            page_obj = paginator.get_page(page_number)

            # Return the results directly (not from DB)
            return Response({
                "results": list(page_obj.object_list),
                "has_next": page_obj.has_next(),
                "has_previous": page_obj.has_previous(),
                "current_page": page_obj.number,
                "total_pages": page_obj.paginator.num_pages,
                "saved_flight_ids": saved_flights
            }, status=200)

        except Exception as e:
            print(f"Error in search_flights: {str(e)}")
            # Return mock data with error message
            return Response({
                "results": [{
                    "airline": "Mock Airline",
                    "route": f"{origin}-{destination}",
                    "date": departure_date,
                    "time": {"departure": "09:00:00", "arrival": "11:00:00"},
                    "price": {"amount": 299.99, "currency": "USD"},
                    "aircraft": "Boeing 737",
                    "note": f"API error: {str(e)}"
                }],
                "has_next": False,
                "has_previous": False,
                "current_page": 1,
                "total_pages": 1,
                "message": "API error. Using mock data."
            }, status=200)

    # Handle GET requests by returning empty results
    else:
        return Response({
            "results": [],
            "message": "Please use POST method for flight search"
        }, status=200)


@api_view(["GET"])
def filter_and_sort_flights(request):
    """
    Filter and sort flights based on query parameters.
    Query parameters:
    - flight_class: Filter by flight class (economy, business, etc.)
    - airline: Filter by airline name
    - sort: Sort by price, departure_time, or duration
    """
    # Get query parameters
    flight_class = request.query_params.get("flight_class", "")
    airline = request.query_params.get("airline", "")
    sort_option = request.query_params.get("sort", "")

    # Start with all flights
    qs = Flight.objects.all()

    # Add origin/destination/date filters if present
    origin = request.query_params.get("origin", "")
    destination = request.query_params.get("destination", "")
    date = request.query_params.get("date", "") or request.query_params.get("departure_date", "")

    if origin:
        qs = qs.filter(origin__icontains=origin)
    if destination:
        qs = qs.filter(destination__icontains=destination)
    if date:
        try:
            date_obj = datetime.strptime(date, "%Y-%m-%d").date()
            qs = qs.filter(departure_date=date_obj)
        except ValueError:
            # Invalid date format, ignore this filter
            pass

    # Apply class and airline filters if provided
    if flight_class:
        qs = qs.filter(flight_class__iexact=flight_class)
    if airline:
        qs = qs.filter(airline__icontains=airline)

    # Apply sorting
    if sort_option == "price":
        qs = qs.order_by("price")
    elif sort_option == "departure_time":
        qs = qs.order_by("departure_date", "departure_time")
    elif sort_option == "duration":
        # Duration sorting is more complex as it's calculated
        # First convert to list and sort manually
        flights_list = list(qs)

        def get_duration(flight):
            # Calculate duration in minutes for sorting
            if not flight.departure_time or not flight.arrival_time:
                return 9999  # Large number for unknown durations

            # Create datetime objects for departure and arrival
            if flight.departure_date and flight.arrival_date:
                d_datetime = datetime.combine(flight.departure_date, flight.departure_time)
                a_datetime = datetime.combine(flight.arrival_date, flight.arrival_time)
            else:
                # If dates are missing, assume same-day flight
                today = datetime.now().date()
                d_datetime = datetime.combine(today, flight.departure_time)
                a_datetime = datetime.combine(today, flight.arrival_time)

            # Handle overnight flights
            if a_datetime < d_datetime:
                a_datetime = a_datetime.replace(day=a_datetime.day + 1)

            # Calculate duration in minutes
            duration = (a_datetime - d_datetime).total_seconds() / 60
            return duration

        flights_list.sort(key=get_duration)

        # Convert sorted list to serializer-friendly format
        serializer = FlightSerializer(flights_list, many=True)
        return Response(serializer.data)
    else:
        # Default sort by departure date and time
        qs = qs.order_by("departure_date", "departure_time")

    # Serialize and return the filtered/sorted results
    serializer = FlightSerializer(qs, many=True)
    return Response(serializer.data)


def remove_duplicate_flights(flight_list):
    """
    Remove duplicate flights based on key properties
    """
    # Use a dictionary to track unique flights
    unique_flights = {}

    # Process each flight
    for flight in flight_list:
        # Create keys based on important properties
        airline = flight.get('airline', '')
        route = flight.get('route', '')
        date = flight.get('date', '')
        departure = flight.get('time', {}).get('departure', '')
        arrival = flight.get('time', {}).get('arrival', '')
        price = str(flight.get('price', {}).get('amount', ''))

        # Create a unique key
        unique_key = f"{airline}|{route}|{date}|{departure}|{arrival}|{price}"

        # Only keep one flight per unique key
        if unique_key not in unique_flights:
            unique_flights[unique_key] = flight

    # Return the deduplicated list
    return list(unique_flights.values())


def search_view(request):
    """
    Render the search page with flights from the database if available
    """
    page = request.GET.get('page', 1)
    try:
        page = int(page)
    except (ValueError, TypeError):
        page = 1

    # Check if we have search parameters
    if request.GET.get('origin') and request.GET.get('destination'):
        origin = request.GET.get('origin')
        destination = request.GET.get('destination')
        date = request.GET.get('date') or request.GET.get('departure_date')

        # Try to get flights from the database
        flight_query = Flight.objects.filter(
            origin__icontains=origin,
            destination__icontains=destination
        )

        # Add date filter if provided
        if date:
            try:
                date_obj = datetime.strptime(date, "%Y-%m-%d").date()
                flight_query = flight_query.filter(departure_date=date_obj)
            except ValueError:
                # Invalid date format, ignore this filter
                pass

        # Apply any additional filters from request
        flight_class = request.GET.get('flight_class', '')
        airline = request.GET.get('airline', '')
        sort = request.GET.get('sort', '')

        if flight_class:
            flight_query = flight_query.filter(flight_class__iexact=flight_class)
        if airline:
            flight_query = flight_query.filter(airline__icontains=airline)

        # Apply sorting
        if sort == 'price':
            flight_query = flight_query.order_by('price')
        elif sort == 'departure_time':
            flight_query = flight_query.order_by('departure_date', 'departure_time')
        else:
            # Default sort
            flight_query = flight_query.order_by('departure_date', 'departure_time')

        # Apply pagination
        paginator = Paginator(flight_query, 10)  # Show 10 flights per page
        try:
            page_obj = paginator.page(page)
        except (EmptyPage, PageNotAnInteger):
            page_obj = paginator.page(1)

        return render(request, "search.html", {
            "flights": page_obj,
            "page_obj": page_obj,
            "current_page": page,
            "total_pages": paginator.num_pages
        })
    else:
        # No search parameters provided
        return render(request, "search.html", {
            "flights": [],
            "current_page": 1,
            "total_pages": 1
        })


def parse_price(raw_str):
    """
    Strip out everything except digits and dots, then convert to Decimal.
    """
    numeric_str = re.sub(r'[^0-9\.]+', '', str(raw_str))
    if not numeric_str:
        numeric_str = '0.00'
    return Decimal(numeric_str)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def save_trip(request):
    try:
        trip_data = request.data.get("trip_data", {})
        if not trip_data:
            return Response({"error": "Missing trip_data"}, status=400)

        price_data = trip_data.get("price", {})
        amount_str = price_data.get("amount", "0")  # e.g. "257"
        currency = price_data.get("currency", "USD")  # e.g. "USD"

        decimal_price = parse_price(amount_str)

        saved_trip = SavedTrip.objects.create(
            user=request.user,
            trip_data=trip_data,
            price=decimal_price,  # must be Decimal or numeric
            currency=currency or "USD",  # assign currency string
            origin=trip_data.get("origin", ""),
            destination=trip_data.get("destination", ""),
            airline=trip_data.get("airline", "Unknown"),
            date=trip_data.get("date", ""),
            aircraft=trip_data.get("aircraft", "Unknown"),
        )

        return Response({
            "message": "Trip saved successfully",
            "saved_trip_id": saved_trip.id
        }, status=200)
    except Exception as e:
        print(f"Error saving trip: {str(e)}")
        return Response({"error": f"Failed to save trip: {str(e)}"}, status=500)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def check_saved_trips(request):
    user = request.user
    saved_trips = SavedTrip.objects.filter(user=user)
    api = BookAPI()
    notifications_created = []

    for saved_trip in saved_trips:
        try:
            trip_data = saved_trip.trip_data
            saved_price = Decimal(trip_data.get("price", {}).get("amount", 0))
            if saved_price == 0:
                continue

            origin = trip_data.get("origin")
            destination = trip_data.get("destination")
            departure_date = trip_data.get("date")
            flight_class = trip_data.get("flight_class", "economy")
            airline = trip_data.get("airline", "")

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

            if current_flights and len(current_flights) > 0 and len(current_flights[0]) > 0:
                current_info = current_flights[0][0]
                current_price = Decimal(current_info.get("price", {}).get("amount", 0))

                if current_price <= saved_price * Decimal('0.95'):
                    message = (
                        f"Price drop alert: Your saved trip from {origin} to {destination} "
                        f"has dropped from {saved_price} to {current_price} "
                        f"{current_info.get('price', {}).get('currency', 'USD')}."
                    )
                    Notification.objects.create(user=user, message=message)
                    notifications_created.append(message)
            else:
                continue

        except Exception as e:
            print(f"Error checking saved trip {saved_trip.id}: {e}")
            continue

    if notifications_created:
        return Response({"notifications": notifications_created}, status=200)
    else:
        return Response({"message": "No price drops detected at this time."}, status=200)