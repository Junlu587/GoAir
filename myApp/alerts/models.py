from django.contrib.auth import get_user_model
from django.db import models

# Create your models here.
from django.db import models
from django.utils import timezone

from myApp.flights.models import Flight

# NEW
User = get_user_model()


class Alert(models.Model):
    title = models.CharField(max_length=200)  # 提醒标题
    message = models.TextField()  # 提醒内容
    created_at = models.DateTimeField(default=timezone.now)  # 创建时间
    is_read = models.BooleanField(default=False)  # 是否已读

    # NEW

    departure_date = models.DateTimeField(null=True, blank=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="alerts", null=True, blank=True)  # 关联用户
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name="alerts", null=True, blank=True)  # 关联航班
    target_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # 用户设定的目标价格

    # MODIFY
    def __str__(self):
        return f"{self.title} {self.user.username} - {self.flight.flight_number} (${self.target_price})"
