from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Flight,  SavedTrip

@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = ['flight_number', 'airline', 'origin', 'destination', 'departure_time', 'arrival_time', 'price', 'available_seats']
    search_fields = ['flight_number', 'airline', 'origin', 'destination']
    list_filter = ['airline', 'origin', 'destination']
    ordering = ['departure_time']

@admin.register(SavedTrip)
class SavedTripAdmin(admin.ModelAdmin):
    list_display = ('user', 'trip_info',  'created_at')
    search_fields = ('user__username', 'flight__flight_number')

    def trip_info(self, obj):
        if obj.trip_data:
            origin = obj.trip_data.get('origin', '')
            destination = obj.trip_data.get('destination', '')
            return f"{origin} → {destination}"
        return "-"

    trip_info.short_description = "Trip"