from rest_framework import serializers
from .models import Flight

class FlightSerializer(serializers.ModelSerializer):
    duration = serializers.SerializerMethodField()

    class Meta:
        model = Flight
        fields = [
            'id', 'airline', 'flight_number', 'origin', 'destination',
            'departure_date', 'departure_time', 'arrival_date', 'arrival_time',
            'price', 'currency', 'available_seats', 'stops', 'aircraft',
            'flight_token', 'flight_class', 'duration'
        ]
        extra_kwargs = {
            'available_seats': {'read_only': True},  # Prevent manual changes to available seats
            'flight_token': {'read_only': True}  # Prevent modification of flight token
        }

    def get_duration(self, obj):
        # Return flight duration in hours if available, else None.
        return obj.duration.total_seconds() / 3600 if obj.duration else None
