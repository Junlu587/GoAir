from django.urls import path

from . import views
from .views import trip_list, trip_detail, add_trip, edit_trip, delete_trip


urlpatterns = [
    path('', views.trip_list, name='trip_list'),  # 这样 /trips/ 会匹配 views.trips_list
    path('<int:trip_id>/', trip_detail, name='trip_detail'),  # 详情页
    path('add/', add_trip, name='add_trip'),  # 添加新 Trip
    path('<int:trip_id>/edit/', edit_trip, name='edit_trip'),  # 编辑 Trip
    path('<int:trip_id>/delete/', delete_trip, name='delete_trip'),  # 删除 Trip
]
