import os
from celery import Celery

# 设置 Django 的默认配置
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "GoAir.settings")  # 确保路径正确

# 创建 Celery 实例
app = Celery("GoAir")  # 使用项目名称

# 从 Django `settings.py` 里导入 Celery 配置
app.config_from_object("django.conf:settings", namespace="CELERY")

# 自动发现 Django Apps 里的任务
app.autodiscover_tasks()


@app.task
def debug_task():
    print("✅ Celery 任务运行成功！")


# ✨ 添加 Celery 定时任务（beat）
from celery.schedules import crontab

app.conf.beat_schedule = {
    "check_trip_prices_every_hour": {
        "task": "myApp.trips.tasks.check_all_trip_prices",  # 定时检查机票价格
        "schedule": crontab(minute=0, hour="*"),  # 每小时执行一次
    },
}
