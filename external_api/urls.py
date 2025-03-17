from django.urls import path
from .views import ExternalAPIViewSet

urlpatterns = [
    path('flight-search/', ExternalAPIViewSet.as_view({'get': 'flight_search'}), name='flight-search'),
    path('airport-search/', ExternalAPIViewSet.as_view({'get': 'airport_search'}), name='airport-search'),  # ✅ 添加 airport-search
]
