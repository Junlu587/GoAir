from django.db import models
from django.contrib.auth import get_user_model
from flights.models import Flight  # 关联航班

User = get_user_model()

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookings")  # 预订用户
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name="bookings")  # 预订的航班
    booking_date = models.DateTimeField(auto_now_add=True)  # 预订时间
    status = models.CharField(max_length=20, choices=[("confirmed", "Confirmed"), ("canceled", "Canceled")], default="confirmed")  # 预订状态

    def __str__(self):
        return f"{self.user.username} - {self.flight.flight_number} ({self.status})"
