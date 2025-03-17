from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NotificationViewSet

router = DefaultRouter()
router.register(r'', NotificationViewSet)  # ✅ 只保留 '', 不再写 'notifications/'

urlpatterns = [
    path('', include(router.urls)),
]
