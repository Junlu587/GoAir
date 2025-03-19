from rest_framework import serializers
from .models import Trip


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trip
        fields = ['id', 'user', 'flight_number', 'departure_date', 'status']
