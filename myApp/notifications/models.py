from django.contrib.auth import get_user_model
from django.db import models

# Create your models here.
from django.db import models

# NEW
User = get_user_model()


class Notification(models.Model):
    # MODIFY
    flight = models.ForeignKey('flights.Flight', on_delete=models.CASCADE)
    target_price = models.DecimalField(max_digits=10, decimal_places=2)

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")  # 关联用户
    message = models.TextField()  # 通知内容
    created_at = models.DateTimeField(auto_now_add=True)  # 创建时间
    is_read = models.BooleanField(default=False)  # 是否已读

    def __str__(self):
        return f"Alert for {self.user.username} on {self.flight.flight_number}- {self.message[:50]}"
