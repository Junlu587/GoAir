from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from myApp.alerts.models import Alert
from myApp.notifications.models import Notification
from myApp.trips.models import Trip


#  行程变更
@receiver(post_save, sender=Trip)
def trip_update_notification(sender, instance, created, **kwargs):
    if created:  # 新建时不检查
        return

    try:
        old_trip = Trip.objects.get(pk=instance.pk)
    except Trip.DoesNotExist:
        return

    # 调用封装好的方法
    instance.generate_update_notifications(old_trip)


# 🚀 **信号（Signal）：当 Trip 价格更新时，自动调用 check_price_drop**
@receiver(pre_save, sender=Trip)
def check_price_drop(sender, instance, **kwargs):
    # """
    # 当 Trip 的价格发生变化时：
    #   1. 如果新价格 < 原价，则提醒“价格已下降”
    #   2. 如果新价格 < target_price，则提醒“已低于目标价”
    # """
    if not instance.pk:
        return  # 新建时不比较
    try:
        old_trip = Trip.objects.get(pk=instance.pk)
    except Trip.DoesNotExist:
        return

        # 如果价格没变，就不做任何事
    if old_trip.current_price == instance.current_price:
        return

        # 调用我们刚才写好的方法
    instance.check_and_create_price_alerts(old_price=old_trip.current_price)