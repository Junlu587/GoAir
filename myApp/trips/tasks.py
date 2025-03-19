# myApp/trips/tasks.py
from celery import shared_task
from myApp.trips.models import Trip
from myApp.alerts.models import Alert


@shared_task
def check_price_drops():
    trips = Trip.objects.all()
    for trip in trips:
        # 在定时任务中，old_price 也可以直接传 trip.original_price
        trip.check_and_create_price_alerts(old_price=trip.original_price)
    return "Price checks completed."
