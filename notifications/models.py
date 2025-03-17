from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")  # 关联用户
    message = models.TextField()  # 通知内容
    created_at = models.DateTimeField(auto_now_add=True)  # 创建时间
    is_read = models.BooleanField(default=False)  # 是否已读

    def __str__(self):
        return f"{self.user.username} - {self.message[:50]}"
