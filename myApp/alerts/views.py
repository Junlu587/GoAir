from django.contrib.auth.decorators import login_required
from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from rest_framework import viewsets, permissions
from rest_framework.authentication import SessionAuthentication, TokenAuthentication

from .models import Alert
from .serializers import AlertSerializer


@login_required  # 🚀 确保用户已登录才能访问提醒页面
def alerts_view(request):
    alerts = Alert.objects.all().order_by('-created_at')  # 获取所有提醒
    return render(request, 'alerts.html', {'alerts': alerts})


# NEW
class AlertViewSet(viewsets.ModelViewSet):
    # """
    # 🚀 API 端点：只能获取 & 操作当前用户的提醒
    # """
    serializer_class = AlertSerializer
    permission_classes = [permissions.IsAuthenticated]  # 只允许登录用户访问
    authentication_classes = [SessionAuthentication, TokenAuthentication]  # 支持会话 & Token 认证

    def get_queryset(self):
        # """
        # 🚀 让 API 只返回当前用户的提醒
        # """
        return Alert.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # """
        # 🚀 创建提醒时，自动关联到当前用户
        # """
        serializer.save(user=self.request.user)
