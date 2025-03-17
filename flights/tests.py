# test_book.py
"""
This script tests the BookAPI integration.
Run this file with:
    python test_book.py
It will call the BookAPI's search_flights method with sample parameters.
"""
from django.test import TestCase
from external_api.book import BookAPI # Absolute import

class BookAPITest(TestCase):
    def test_search_flights(self):
        api = BookAPI()
        results = api.search_flights(
            origin="beijing",
            destination="shanghai",
            trip_type="oneway",
            date="2025-04-01",
            return_date="2025-04-15",
            flight_class="economy",
            airline="UA",
            sort="BEST"
        )
        self.assertIsNotNone(results)
