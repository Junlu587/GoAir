# NEW
from rest_framework import serializers
from .models import Alert


class AlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alert
        # ATTENTION
        fields = ['id', 'user', 'flight', 'target_price', 'created_at']
        read_only_fields = ['user', 'created_at']

