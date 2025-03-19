# NEW
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(
        required=False,
        validators=[RegexValidator(regex=r'^\+?\d{7,15}$', message="请输入有效的电话号码")]
    )

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone', 'password', 'avatar']
        extra_kwargs = {
            'password': {'write_only': True},
            'is_staff': {'read_only': True},
            'is_superuser': {'read_only': True},
        }

    def validate_password(self, value):
        if len(value) < 6:
            raise serializers.ValidationError("The password must be at least 6 characters long!")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
