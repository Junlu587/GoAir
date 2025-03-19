from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views
from .views import UserViewSet

urlpatterns = [
    # ========== 修改处：新增 check_user 路由 ==========
    path('check_user/', views.check_user, name='check_user'),
]

# NEW
router = DefaultRouter()
router.register(r'', UserViewSet)
router.register(r'', UserViewSet, basename="users")