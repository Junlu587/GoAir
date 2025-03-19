from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

# Create your models here.
from django.db import models


class CustomUser(AbstractUser):
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    # NEW
    phone = models.CharField(max_length=20, blank=True, null=True, unique=True)
    # 新增头像字段
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, default="avatars/default.jpg")
    # 解决冲突：添加 `related_name`
    groups = models.ManyToManyField(Group, related_name="customuser_groups", blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="customuser_permissions", blank=True)

    class Meta:
        swappable = 'AUTH_USER_MODEL'

    def __str__(self):
        return self.username  # 让 Django Admin 显示用户名
