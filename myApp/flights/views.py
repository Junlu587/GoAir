from datetime import datetime
from decimal import Decimal
import json

from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from myApp.external_api.book import BookAPI
from myApp.flights.models import Flight
from myApp.flights.serializers import FlightSerializer
from .models import SavedTrip
from myApp.notifications.models import Notification


@csrf_exempt
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def search_flights(request):
    # Debug print to confirm the view is being called
    print("search_flights called, method:", request.method)

    # Disable CSRF enforcement explicitly
    request._dont_enforce_csrf_checks = True

    if request.method == 'GET':
        origin = request.GET.get('origin')
        destination = request.GET.get('destination')
        departure_date = request.GET.get('departure_date')
        return_date = request.GET.get("return_date")
        flight_class = request.GET.get("flight_class")
        airline = request.GET.get("airline")
        flights = Flight.objects.filter(
            origin=origin,
            destination=destination,
            departure_date=departure_date,
            return_date=return_date,
            flight_class=flight_class,
            airline=airline,
        )
        results = list(flights.values())
        return Response({'results': results})

    elif request.method == 'POST':
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

        if isinstance(flight_results, dict) and "error" in flight_results:
            return Response({"error": flight_results["error"]}, status=502)

        if flight_results is None:
            return Response({"error": "No flights found or API error"}, status=500)

        # Flatten flight_results if it's a list of lists
        flattened = []
        for flist in flight_results:
            flattened.extend(flist)

        # Apply pagination (6 results per page)
        page_number = request.query_params.get("page") or request.data.get("page")
        paginator = Paginator(flattened, 6)
        page_obj = paginator.get_page(page_number)

        # OPTIONAL: store flights in DB
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

                f_date = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else None
                d_time = datetime.strptime(departure_str, "%H:%M:%S").time() if departure_str else None
                a_time = datetime.strptime(arrival_str, "%H:%M:%S").time() if arrival_str else None

                gen_number = "API" + datetime.now().strftime("%H%M%S")

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

        return Response({
            "results": list(page_obj.object_list),
            "has_next": page_obj.has_next(),
            "has_previous": page_obj.has_previous(),
            "current_page": page_obj.number,
            "total_pages": page_obj.paginator.num_pages,
            "saved_flight_ids": saved_flights,
            "raw_api_data": flight_results,
        }, status=200)

    except Exception as e:
        return Response({"error": str(e)}, status=500)


@api_view(["GET"])
def filter_and_sort_flights(request):
    flight_class = request.query_params.get("flight_class")
    airline = request.query_params.get("airline")
    sort_option = request.query_params.get("sort")
    qs = Flight.objects.all()

    if flight_class:
        qs = qs.filter(flight_class__iexact=flight_class)
    if airline:
        qs = qs.filter(airline__iexact=airline)

    if sort_option == "price":
        qs = qs.order_by("price")
    elif sort_option == "departure_time":
        qs = qs.order_by("departure_date", "departure_time")
    elif sort_option == "duration":
        qs = list(qs)
        qs.sort(key=lambda f: f.duration if f.duration is not None else datetime.max - datetime.min)
    else:
        qs = qs.order_by("departure_date", "departure_time")

    serializer = FlightSerializer(qs, many=True)
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def save_trip(request):
    trip_data = request.data.get("trip_data")
    if not trip_data:
        return Response({"error": "Missing trip_data"}, status=400)

    flight_id = trip_data.get("flight_id")
    if not flight_id:
        return Response({"error": "Missing flight_id in trip_data"}, status=400)
    try:
        from flights.models import Flight
        flight_instance = Flight.objects.get(pk=flight_id)
    except Flight.DoesNotExist:
        return Response({"error": "Flight not found"}, status=400)

    saved_trip = SavedTrip.objects.create(user=request.user, trip_data=trip_data)

    return Response({
        "message": "Trip saved successfully",
        "saved_trip_id": saved_trip.id
    }, status=200)


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
