from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views
from .views import NotificationViewSet

urlpatterns = [
    path('', views.notifications, name='notifications'),
]

# NEW
router = DefaultRouter()
router.register(r'', NotificationViewSet)
