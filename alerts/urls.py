from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PriceAlertViewSet

router = DefaultRouter()
router.register(r'', PriceAlertViewSet)  # ✅ 只保留 '', 不再写 'alerts/'

urlpatterns = [
    path('', include(router.urls)),
]
 
