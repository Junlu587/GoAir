from django.urls import path
from .views import ExternalAPIViewSet

urlpatterns = [
    path('flight_search/', ExternalAPIViewSet.as_view({'get': 'flight_search'}), name='flight_search'),
    path('airport_search/', ExternalAPIViewSet.as_view({'get': 'airport_search'}), name='airport_search'),  # ✅ 添加 airport-search
]
