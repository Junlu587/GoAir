# myApp/flights/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import datetime
from .models import SavedTrip
from myApp.trips.models import Trip


@receiver(post_save, sender=SavedTrip)
def create_trip_from_saved_trip(sender, instance, created, **kwargs):
    if created:
        trip_data = instance.trip_data  # 假设 trip_data 是一个包含航班信息的 JSON 字段

        # 提取并转换日期格式（假设日期以 'YYYY-MM-DD' 格式存储）
        departure_date_str = trip_data.get('departure_date')
        return_date_str = trip_data.get('return_date')
        try:
            departure_date = datetime.strptime(departure_date_str, '%Y-%m-%d')
        except Exception:
            departure_date = None
        try:
            return_date = datetime.strptime(return_date_str, '%Y-%m-%d') if return_date_str else None
        except Exception:
            return_date = None

        # 创建 Trip 对象。字段名称要与 Trip 模型保持一致，
        # 需要根据实际情况调整字段名和数据转换。
        Trip.objects.create(
            user=instance.user,
            flight_number=trip_data.get('flight_number', ''),
            origin=trip_data.get('origin', ''),
            destination=trip_data.get('destination', ''),
            departure_date=departure_date,
            return_date=return_date,
            current_price=trip_data.get('price', 0),
            original_price=trip_data.get('price', 0),
            target_price=trip_data.get('target_price', 0),
            airline_company=trip_data.get('airline', '')
        )
