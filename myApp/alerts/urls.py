from django.urls import path
# NEW
from rest_framework.routers import DefaultRouter

from .views import alerts_view, AlertViewSet

urlpatterns = [
    path('', alerts_view, name='alerts'),

]

# NEW
router = DefaultRouter()
router.register(r'alerts', AlertViewSet, basename='alert')
