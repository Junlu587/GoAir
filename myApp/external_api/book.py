import requests
import http.client
import json
import time
from datetime import datetime


class BookAPI:
    def __init__(self):
        self.headers = {
            "x-rapidapi-key": "763ac69eb6msh793e9d528a2bddbp1f4d8ajsn8dac6a73a4d7",  # Your API key
            "x-rapidapi-host": "booking-com15.p.rapidapi.com"
        }
        self.conn = http.client.HTTPSConnection("booking-com15.p.rapidapi.com")

    def search_destination(self, query):
        """Search for airport/location by name"""
        try:
            # Normalize query
            query = query.strip().lower()
            print(f"Searching for destination with query: {query}")

            # Make API request
            self.conn.request("GET", f"/api/v1/flights/searchDestination?query={query}", headers=self.headers)
            res = self.conn.getresponse()
            data = res.read()

            if res.status != 200:
                print(f"Search destination request failed: {res.status} {res.reason}")
                print(data.decode("utf-8"))
                return None

            search_results = json.loads(data.decode("utf-8"))
            print(f"Found {len(search_results.get('data', []))} destination results for query: {query}")

            # Debug the first result
            if search_results.get('data') and len(search_results['data']) > 0:
                first_result = search_results['data'][0]
                print(f"First result: {first_result.get('id')} - {first_result.get('name')}")

            return search_results
        except Exception as e:
            print(f"Error in search_destination: {str(e)}")
            return None

    def extract_flight_info(self, search_results):
        """
        Extract flight information from search results with better error handling
        """
        flights = []

        # Check if search results are valid
        if not search_results or 'data' not in search_results:
            print("Invalid search results format in extract_flight_info")
            return flights

        segments = search_results['data'].get('segments', [])
        total_price = search_results['data'].get('priceBreakdown', {}).get('total', {})

        print(f"Extracting flight info from {len(segments)} segments")

        for segment in segments:
            flight = {}

            try:
                # Extract date and time
                departure_datetime = segment.get('departureTime', '')
                arrival_datetime = segment.get('arrivalTime', '')

                if departure_datetime and 'T' in departure_datetime:
                    flight['date'] = departure_datetime.split('T')[0]
                    flight['time'] = {
                        'departure': departure_datetime.split('T')[1],
                        'arrival': arrival_datetime.split('T')[1] if 'T' in arrival_datetime else '00:00:00'
                    }
                else:
                    # Use current date as fallback
                    today = datetime.now().strftime("%Y-%m-%d")
                    flight['date'] = today
                    flight['time'] = {'departure': '00:00:00', 'arrival': '00:00:00'}

                # Extract route information
                origin = segment.get('departureAirport', {}).get('cityName', 'Unknown')
                destination = segment.get('arrivalAirport', {}).get('cityName', 'Unknown')
                flight['route'] = f"{origin}-{destination}"

                # Extract airline information
                if 'legs' in segment and len(segment['legs']) > 0:
                    leg = segment['legs'][0]
                    carriers = leg.get('carriersData', [])
                    if carriers and len(carriers) > 0:
                        flight['airline'] = carriers[0].get('name', 'Unknown')
                        flight['aircraft'] = leg.get('flightInfo', {}).get('planeType', 'Unknown')
                    else:
                        flight['airline'] = 'Unknown'
                        flight['aircraft'] = 'Unknown'
                else:
                    flight['airline'] = 'Unknown'
                    flight['aircraft'] = 'Unknown'

                # Extract price information
                flight['price'] = {
                    'amount': total_price.get('units', 0),
                    'currency': total_price.get('currencyCode', 'USD')
                }

                flights.append(flight)

            except Exception as e:
                print(f"Error extracting flight info from segment: {str(e)}")
                continue

        return flights

    def get_flight_info(self, token):
        """Get detailed flight information using a token"""
        if not token:
            print("Error: Null token provided to get_flight_info")
            return None

        try:
            print(f"Getting flight details for token: {token[:10]}...")

            # Make API request
            self.conn.request("GET", f"/api/v1/flights/getFlightDetails?token={token}&currency_code=USD",
                              headers=self.headers)
            res = self.conn.getresponse()
            data = res.read()

            if res.status != 200:
                print(f"Flight details request failed: {res.status} {res.reason}")
                print(data.decode("utf-8"))
                return None

            search_results = json.loads(data.decode("utf-8"))

            # Debug the response structure
            print(f"Flight details response keys: {list(search_results.keys())}")
            if 'data' in search_results:
                print(f"Flight data keys: {list(search_results['data'].keys())}")

            flight_info = self.extract_flight_info(search_results)
            print(f"Extracted {len(flight_info)} flights from details")

            return flight_info
        except Exception as e:
            print(f"Error in get_flight_info: {str(e)}")
            return None

    def search_flights(self, origin, destination, trip_type, date, return_date, flight_class, airline, sort):
        """
        Search for flights with the given parameters
        """
        print(f"Searching flights: {origin} to {destination} on {date}")

        try:
            # Look up origin and destination
            ori_results = self.search_destination(origin)
            if not ori_results or 'data' not in ori_results or not ori_results['data']:
                print(f"No origin airports found for '{origin}'")
                return self._generate_mock_flight(origin, destination, date, "No origin airports found")

            dest_results = self.search_destination(destination)
            if not dest_results or 'data' not in dest_results or not dest_results['data']:
                print(f"No destination airports found for '{destination}'")
                return self._generate_mock_flight(origin, destination, date, "No destination airports found")

            # Get IDs from the first result
            fromId = ori_results['data'][0]['id']
            toId = dest_results['data'][0]['id']

            print(f"Using fromId: {fromId}, toId: {toId}")

            # Normalize flight class
            flight_class = flight_class.upper() if flight_class else "ECONOMY"

            # Build parameters
            params = {
                "fromId": fromId,
                "toId": toId,
                "sort": sort or "BEST",
                "cabinClass": flight_class,
                "departDate": date,
                "returnDate": return_date or "",
                "pageNo": 1,
                "adults": 1,
                "children": "0",
                "currency_code": "USD"
            }

            print(f"Search parameters: {params}")

            # Build query string and make API request
            query_string = "&".join([f"{k}={v}" for k, v in params.items()])
            request_path = f"/api/v1/flights/searchFlights?{query_string}"

            print(f"Making API request to: {request_path}")
            self.conn.request("GET", request_path, headers=self.headers)

            res = self.conn.getresponse()
            data = res.read()
            decoded_data = data.decode("utf-8")

            # Handle non-200 responses
            if res.status != 200:
                print(f"Search flights request failed: {res.status} {res.reason}")
                print(f"Response: {decoded_data[:500]}...")  # Print first 500 chars of response
                return self._generate_mock_flight(origin, destination, date, f"API Error: {res.status} {res.reason}")

            search_results = json.loads(decoded_data)

            # Debug the response structure
            if 'error' in search_results:
                error_msg = search_results.get('error', '')
                error_desc = search_results.get('description', '')
                print(f"API returned error: {error_msg}")
                print(f"Error description: {error_desc}")
                return self._generate_mock_flight(origin, destination, date, error_msg)

            # Validate search results structure
            if 'data' not in search_results:
                print("Missing 'data' field in search results")
                print(f"Response keys: {list(search_results.keys())}")
                return self._generate_mock_flight(origin, destination, date, "Invalid API response format")

            if 'flightOffers' not in search_results['data'] or not search_results['data']['flightOffers']:
                print("No flight offers found in search results")
                return self._generate_mock_flight(origin, destination, date, "No flights found")

            # Process flight offers
            offers = search_results['data']['flightOffers']
            print(f"Found {len(offers)} flight offers")

            flight_list = []
            for i, offer in enumerate(offers[:10]):  # Process first 10 offers max
                token = offer.get('token')
                if not token:
                    print(f"Offer {i} has no token, skipping")
                    continue

                print(f"Processing offer {i + 1} with token: {token[:10]}...")
                info = self.get_flight_info(token)

                if info:
                    flight_list.append(info)
                    print(f"Added flight info for offer {i + 1}")
                else:
                    print(f"Failed to get flight info for offer {i + 1}")

                # Small delay to avoid API rate limits
                if i < len(offers) - 1:
                    time.sleep(0.2)

            if flight_list:
                print(f"Returning {len(flight_list)} flights")
                return flight_list
            else:
                print("No flight details could be retrieved")
                return self._generate_mock_flight(origin, destination, date, "Failed to retrieve flight details")

        except Exception as e:
            print(f"Exception in search_flights: {str(e)}")
            import traceback
            traceback.print_exc()
            return self._generate_mock_flight(origin, destination, date, f"Exception: {str(e)}")

    def _generate_mock_flight(self, origin, destination, date, error_msg=None):
        """Generate mock flight data with optional error message"""
        mock_flight = [{
            "airline": "Mock Airline",
            "flight_number": "MOCK123",
            "route": f"{origin}-{destination}",
            "date": date,
            "time": {"departure": "09:00:00", "arrival": "11:00:00"},
            "price": {"amount": 199.99, "currency": "USD"},
            "aircraft": "Boeing 737"
        }]

        if error_msg:
            mock_flight[0]["note"] = f"Mock data - {error_msg}"
        else:
            mock_flight[0]["note"] = "Mock data (API unavailable)"

        return [mock_flight]


# For testing purposes
if __name__ == "__main__":
    api = BookAPI()
    # Test the API with sample data
    print(api.search_flights(
        "beijing",
        "shanghai",
        "oneway",
        "2025-04-01",
        "2025-04-15",
        "economy",
        "UA",
        "BEST"
    ))