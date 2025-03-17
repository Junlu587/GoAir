from rest_framework import viewsets, permissions
from .models import PriceAlert
from .serializers import PriceAlertSerializer

class PriceAlertViewSet(viewsets.ModelViewSet):
    queryset = PriceAlert.objects.all()
    serializer_class = PriceAlertSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)  # ✅ 自动关联当前用户
