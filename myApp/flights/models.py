from django.db import models
from django.contrib.auth import get_user_model
import datetime

# Get the User model (custom or default)
User = get_user_model()


class Flight(models.Model):
    airline = models.CharField(max_length=100,default="Unknown Airline")
    flight_number = models.CharField(max_length=10, unique=True, default="UNKNOWN")
    origin = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)

    # Required departure date
    departure_date = models.DateField(default=datetime.date.today)

    # Optional times/dates
    departure_time = models.TimeField(null=True, blank=True)
    arrival_date = models.DateField(null=True, blank=True)
    arrival_time = models.TimeField(null=True, blank=True)
    return_date = models.DateField(null=True, blank=True)

    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    currency = models.CharField(max_length=10, default="USD")
    available_seats = models.PositiveIntegerField(default=100)
    stops = models.IntegerField(default=0)
    aircraft = models.CharField(max_length=100, default="Unknown", blank=True)
    flight_token = models.CharField(max_length=100, null=True, blank=True)
    flight_class = models.CharField(max_length=50, default="economy")

    @property
    def duration(self):
        """
        If departure/arrival date/time are set, returns a timedelta; otherwise None.
        """
        if (
                self.departure_date and self.departure_time and
                self.arrival_date and self.arrival_time
        ):
            departure_dt = datetime.datetime.combine(self.departure_date, self.departure_time)
            arrival_dt = datetime.datetime.combine(self.arrival_date, self.arrival_time)
            return arrival_dt - departure_dt
        return None

    def __str__(self):
        return f"{self.flight_number} - {self.origin} to {self.destination} ({self.departure_time})"


# Add this to your models.py file if not already present

class SavedTrip(models.Model):
    """
    Model to store saved trips from search results
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="saved_trips")
    trip_data = models.JSONField(null=True, blank=True)
    flight = models.ForeignKey('Flight', on_delete=models.CASCADE, related_name="saved_in", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


    # # Add these fields to store important data directly
    origin = models.CharField(max_length=100, default="", null=True, blank=True)
    destination = models.CharField(max_length=100, default="", null=True, blank=True)
    airline = models.CharField(max_length=100, default="Unknown", null=True, blank=True)
    date = models.CharField(max_length=20, default="", null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, null=True, blank=True)
    currency = models.CharField(max_length=10, default="USD", null=True, blank=True)
    aircraft = models.CharField(max_length=100, default="Unknown", null=True, blank=True)

    def __str__(self):
        return f"Saved trip for {self.user.username} at {self.created_at}"
