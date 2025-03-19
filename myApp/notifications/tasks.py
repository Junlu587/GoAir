# myApp/trips/tasks.py
from celery import shared_task
from django.utils.timezone import now, timedelta
from myApp.trips.models import Trip
from myApp.notifications.models import Notification


@shared_task
def send_upcoming_flight_notifications():
    """🔔 发送即将出发航班的通知"""
    upcoming_flights = Trip.objects.filter(
        departure_date__gte=now(),  # 当前时间之后
        departure_date__lte=now() + timedelta(days=1)  # 未来24小时内
    )

    for trip in upcoming_flights:
        Notification.objects.create(
            user=trip.user,
            trip=trip,
            message=f"Reminder: Your flight {trip.flight_number} is departing soon on {trip.departure_date}!"
        )
    return f"Notifications sent for {upcoming_flights.count()} upcoming flights"
