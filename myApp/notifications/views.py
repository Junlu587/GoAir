from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from myApp.notifications.models import Notification
from myApp.notifications.serializers import NotificationSerializer


@login_required
def notifications(request):
    # """
    # 渲染通知页面，展示当前登录用户的所有通知
    # """
    # 获取当前用户的所有通知，按创建时间倒序
    unread_notifications = Notification.objects.filter(user=request.user, is_read=False).order_by("-created_at")
    historical_notifications = Notification.objects.filter(user=request.user, is_read=True).order_by("-created_at")

    return render(request, 'notifications.html', {
        'unread_notifications': unread_notifications,
        'historical_notifications': historical_notifications,
    })


class NotificationViewSet(viewsets.ModelViewSet):
    # """
    # API 视图：管理用户的通知
    # - 仅返回当前用户的通知
    # - 支持筛选（是否已读、与特定行程关联）
    # - 支持批量标记为已读
    # """
    queryset = Notification.objects.all().order_by('-created_at')  # ✅ 解决错误 按时间排序
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # """
        # ⚡ 仅返回当前用户的通知，并支持手动筛选
        # """
        queryset = Notification.objects.filter(user=self.request.user).order_by('-created_at')

        # 手动获取筛选参数
        is_read = self.request.query_params.get('is_read')
        trip = self.request.query_params.get('trip')

        # 根据参数进行筛选
        if is_read in ['true', 'True', '1']:
            queryset = queryset.filter(is_read=True)
        elif is_read in ['false', 'False', '0']:
            queryset = queryset.filter(is_read=False)

        if trip:
            queryset = queryset.filter(trip=trip)

        return queryset

    def perform_create(self, serializer):
        # """创建通知时自动关联用户"""
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['patch'])
    def mark_as_read(self, request, pk=None):
        # """
        # ✅ 标记单个通知为已读
        # """
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'status': 'Notification marked as read'})

    @action(detail=False, methods=['patch'])
    def mark_all_as_read(self, request):
        # """
        # ✅ 批量标记所有未读通知为已读
        # """
        self.get_queryset().filter(is_read=False).update(is_read=True)
        return Response({'status': 'All notifications marked as read'})
