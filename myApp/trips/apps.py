from django.apps import AppConfig


class TripsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'myApp.trips'  # 这里的路径需要与你的项目结构匹配

    def ready(self):
        import myApp.trips.signals  # 确保信号被加载