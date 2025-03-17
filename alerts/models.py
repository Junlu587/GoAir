from django.db import models
from django.contrib.auth import get_user_model
from flights.models import Flight

User = get_user_model()

class PriceAlert(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="alerts")  # 关联用户
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name="alerts")  # 关联航班
    target_price = models.DecimalField(max_digits=10, decimal_places=2)  # 用户设定的目标价格
    created_at = models.DateTimeField(auto_now_add=True)  # 创建时间

    def __str__(self):
        return f"{self.user.username} - {self.flight.flight_number} (${self.target_price})"
