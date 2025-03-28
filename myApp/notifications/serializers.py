from rest_framework import serializers
from .models import Notification


# NEW
class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'user', 'message', 'created_at', 'is_read']
        read_only_fields = ['user', 'created_at']
