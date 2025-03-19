# myApp/flights/apps.py
from django.apps import AppConfig


class FlightsConfig(AppConfig):
    name = 'myApp.flights'

    def ready(self):
        import myApp.flights.signals  # 导入 signals.py 以注册信号处理器
