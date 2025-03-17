from django.urls import path
from .views import search_flights, filter_and_sort_flights, save_trip, check_saved_trips

urlpatterns = [
    path("search/", search_flights, name="flight-search"),  # ✅ 绑定正确的 API 端点
    path("filter/", filter_and_sort_flights, name="flight-filter"),
    path("save_trip/", save_trip, name="save-trip"),
    path("check_saved_trips/", check_saved_trips, name="check-saved-trips"),
]
