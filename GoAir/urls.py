from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('users.urls')),
    path('api/flights/', include('flights.urls')), 
    path('api/bookings/', include('bookings.urls')),
    path('api/alerts/', include('alerts.urls')),
    path('api/notifications/', include('notifications.urls')),
    path("api/external/", include("external_api.urls")),
    path('accounts/', include('allauth.urls')),
]
