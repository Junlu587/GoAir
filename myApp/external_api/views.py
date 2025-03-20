from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from myApp.external_api.book import BookAPI

class ExternalAPIViewSet(viewsets.ViewSet):
    """
    Example ViewSet providing GET endpoints for flight searches.
    """
    permission_classes = [AllowAny]

    def flight_search(self, request):
        """
        GET /api/external/flight-search/
        e.g. ?origin=NYCA&destination=JFK&type=oneway&date=2025-04-01
        """
        origin = request.query_params.get("origin")
        destination = request.query_params.get("destination")
        date = request.query_params.get("departure_date")

        if not origin or not destination or not date:
            return Response({"error": "origin, destination, and date are required"}, status=400)

        # Use defaults for other parameters
        trip_type = request.query_params.get("type", "oneway")
        return_date = request.query_params.get("return_date", "")
        flight_class = request.query_params.get("flight_class", "economy")
        airline = request.query_params.get("airline", "")
        sort = request.query_params.get("sort", "BEST")

        api = BookAPI()
        data = api.search_flights(
            origin=origin,
            destination=destination,
            trip_type=trip_type,
            date=date,
            return_date=return_date,
            flight_class=flight_class,
            airline=airline,
            sort=sort
        )
        return Response(data)

    def airport_search(self, request):
        """
        GET /api/external/airport-search/?query=LAX
        """
        query = request.query_params.get("query", "LAX")
        api = BookAPI()
        data = api.search_destination(query)
        return Response(data)
