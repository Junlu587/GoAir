from rest_framework import serializers
from .models import PriceAlert

class PriceAlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = PriceAlert
        fields = ['id', 'user', 'flight', 'target_price', 'created_at']
        read_only_fields = ['user', 'created_at']
 
