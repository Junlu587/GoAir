import requests
import http.client
import json


class BookAPI:
    def __init__(self):
        self.headers = {
            "x-rapidapi-key": "85ee220e84msha0a35b916c0fae3p1a2cbejsne95a2a9b1b89",  # Your API key
            "x-rapidapi-host": "booking-com15.p.rapidapi.com"
        }
        self.conn = http.client.HTTPSConnection("booking-com15.p.rapidapi.com")

    def search_destination(self, query):
        self.conn.request("GET", f"/api/v1/flights/searchDestination?query={query}", headers=self.headers)
        res = self.conn.getresponse()
        data = res.read()
        if res.status != 200:
            print(f"Search request failure: {res.status} {res.reason}")
            print(data.decode("utf-8"))
            return None
        search_results = json.loads(data.decode("utf-8"))
        return search_results

    def extract_flight_info(self, search_results):

        flights = []
        if not search_results or 'data' not in search_results:
            return flights

        segments = search_results['data'].get('segments', [])
        total_price = search_results['data']['priceBreakdown']['total']
        for segment in segments:
            flight = {}
            # extract date and time
            departure_datetime = segment['departureTime']
            arrival_datetime = segment['arrivalTime']
            flight['date'] = departure_datetime.split('T')[0]
            flight['time'] = {
                'departure': departure_datetime.split('T')[1],
                'arrival': arrival_datetime.split('T')[1]
            }
            # extract airports
            origin = segment['departureAirport']['cityName']
            destination = segment['arrivalAirport']['cityName']
            flight['route'] = f"{origin}-{destination}"
            # extract airlines
            if 'legs' in segment and len(segment['legs']) > 0:
                carriers = segment['legs'][0].get('carriersData', [])
                if carriers:
                    flight['airline'] = carriers[0].get('name', 'Unknown')
                    flight['aircraft'] = segment['legs'][0].get('flightInfo', {}).get('planeType', 'Unknown')
            # extract price
            flight['price'] = {
                'amount': total_price.get('units', 0),
                'currency': total_price.get('currencyCode', 'USD')
            }
            flights.append(flight)
        return flights

    def get_flight_info(self, token):
        conn = self.conn
        conn.request("GET", f"/api/v1/flights/getFlightDetails?token={token}&currency_code=GBP", headers=self.headers)
        res = conn.getresponse()
        data = res.read()
        if res.status != 200:
            print(f"Search request failure: {res.status} {res.reason}")
            print(data.decode("utf-8"))
            return None
        search_results = json.loads(data.decode("utf-8"))
        return self.extract_flight_info(search_results)

    def search_flights(self, origin, destination, trip_type, date, return_date, flight_class, airline, sort):
        try:
            # 1) Query the origin/destination
            ori_results = self.search_destination(origin)
            dest_results = self.search_destination(destination)

            if not ori_results or not dest_results:
                return {"error": "No airport data returned from BookAPI"}

            if len(ori_results.get('data', [])) == 0 or len(dest_results.get('data', [])) == 0:
                return {"error": "No matching airports found in BookAPI"}


            fromId = ori_results['data'][0]['id']
            toId = dest_results['data'][0]['id']
            flight_class = flight_class.upper()

            params = {
                "fromId": fromId,
                "toId": toId,
                "sort": sort,
                "cabinClass": flight_class,
                "departDate": date,
                "returnDate": return_date,
                "pageNo": 1,
                "adults": 1,
                "children": "0",
                "currency_code": "USD"
            }

            query_string = "&".join([f"{k}={v}" for k, v in params.items()])
            self.conn.request("GET", f"/api/v1/flights/searchFlights?{query_string}", headers=self.headers)
            res = self.conn.getresponse()
            data = res.read()
            if res.status != 200:
                print(f"Search request failure: {res.status} {res.reason}")
                print(data.decode("utf-8"))
                return None
            search_results = json.loads(data.decode("utf-8"))

            flight_list = []
            for offer in search_results['data'].get('flightOffers', []):
                token = offer.get('token')
                if token:
                    info = self.get_flight_info(token)
                    flight_list.append(info)
                else:
                    print("Partial data: offer missing token.")
            return flight_list

        except http.client.HTTPException as http_err:
            print(f"HTTP error occurred: {http_err}")
            return {"error": "Failed to connect to BookAPI (HTTPException). Please try again later."}

        except Exception as e:
            print(f"Unexpected error: {e}")
            return {"error": "An unexpected error occurred while fetching flight data."}



