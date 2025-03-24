from django.urls import path
from . import views
from .views import search_flights, filter_and_sort_flights, save_trip, check_saved_trips


app_name = 'flights'
urlpatterns = [
    path("search/", search_flights, name="flight_search"),  # ✅ 绑定正确的 API 端点
    path("filter/", filter_and_sort_flights, name="flight_filter"),
    path('filter_and_sort_flights/', views.filter_and_sort_flights, name='filter_and_sort_flights'),
    path("save_trip/", save_trip, name="save_trip"),
    path("check_saved_trips/", check_saved_trips, name="check_saved_trips"),

]
