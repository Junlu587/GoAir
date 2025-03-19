from dateutil.utils import today
from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import pre_save
from django.dispatch import receiver

from myApp.notifications.models import Notification

User = get_user_model()  # 获取 Django 自定义用户模型


class Trip(models.Model):
    class StatusChoices(models.TextChoices):
        CONFIRMED = "confirmed", "Confirmed"
        CANCELED = "canceled", "Canceled"

    # 关联用户，related_name 让 User 反向访问 trips
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="trips"
    )

    flight_number = models.CharField("Flight Number", max_length=20)
    origin = models.CharField("Origin", max_length=100)
    destination = models.CharField("Destination", max_length=100)
    departure_date = models.DateTimeField("Departure Date")
    return_date = models.DateTimeField("Return Date", null=True, blank=True)
    created_at = models.DateTimeField("Created At", auto_now_add=True)
    current_price = models.DecimalField("Current Price", max_digits=10, decimal_places=2, default=0.00)
    original_price = models.DecimalField("Original Price", max_digits=10, decimal_places=2, default=0.0)  # 记录用户添加时的价格

    # 目标价位必填：去掉 null=True, blank=True
    target_price = models.DecimalField("Target Price", max_digits=10, decimal_places=2)

    # 座位号
    seat_number = models.CharField(max_length=20, null=True, blank=True)

    # 航空公司
    airline_company = models.CharField(max_length=100, null=True, blank=True)

    # 舱位
    class_of_service = models.CharField(max_length=50, null=True, blank=True)

    # 预订状态
    status = models.CharField(
        "Status", max_length=20, choices=StatusChoices.choices, default=StatusChoices.CONFIRMED
    )

    class Meta:
        verbose_name = "Trip"
        verbose_name_plural = "Trips"
        ordering = ["-departure_date"]  # 默认按照出发时间降序排列

    def __str__(self):
        return f"{self.departure_date} | {self.flight_number} | {self.origin} → {self.destination} | {self.get_status_display()}"

    def check_and_create_price_alerts(self, old_price=None):
        """
        检测并创建价格提醒：
          - 若 current_price < old_price => 'Price Dropped!'
          - 若 current_price < target_price => 'Price Below Target!'
        """
        from myApp.alerts.models import Alert  # 避免循环依赖，延迟导入

        old_price = old_price or self.original_price
        # 价格下降
        if self.current_price < old_price:
            Alert.objects.create(
                user=self.user,
                # flight=...  如果有 flight 外键的话，可以加上
                title="Price Dropped!",
                message=(
                    f"Price for flight {self.flight_number} has dropped "
                    f"from {old_price} to {self.current_price}."
                )
            )

        # 情况 B: 价格上涨
        elif self.current_price > old_price:
            Alert.objects.create(
                user=self.user,
                # flight=self.flight,
                title="Price Increased!",
                message=(
                    f"Price for flight {self.flight_number} has increased "
                    f"from {old_price} to {self.current_price}."
                )
        )

        # 低于目标价格
        if self.target_price and self.current_price < self.target_price:
            Alert.objects.create(
                user=self.user,
                # flight=...
                title="Price Below Target!!!",
                message=(
                    f"Price for flight {self.flight_number} is now {self.current_price}, "
                    f"which is below your target of {self.target_price}."
                )
            )

    def generate_update_notifications(self, old_trip):
        """
        对比 old_trip（更新前的数据）和 self（更新后），
        如果航班出发时间或状态有变化，就创建对应的通知
        """
        notifications = []

        # 🚀 出发日期变更
        if old_trip.departure_date != self.departure_date:
            notifications.append(
                f"✈️ Your flight **{self.flight_number}** now departs on **{self.departure_date.strftime('%Y-%m-%d %H:%M')}**."
            )

        # 🚀 航班状态变更
        if old_trip.status != self.status:
            notifications.append(
                f"⚠️ Your flight **{self.flight_number}** status changed to **{self.get_status_display()}**."
            )

        # ✅ 创建通知
        for message in notifications:
            Notification.objects.create(
                user=self.user,
                trip=self,
                message=message
            )
