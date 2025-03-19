from django.contrib.auth import get_user_model, authenticate

# Create your views here.
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from GoAir import settings
from myApp.users.serializers import UserSerializer

# NEW
User = get_user_model()


# NEW
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action in ['create', 'login']:
            return [AllowAny()]
        return [IsAuthenticated()]

    @action(detail=False, methods=['post'])
    def login(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)
        if user:
            return Response({"message": "Login Successful!", "username": user.username})
        return Response({"error": "Incorrect username or password!"}, status=status.HTTP_400_BAD_REQUEST)


# ========== 修改处：新增 check_user 函数 ==========
@api_view(["GET"])
@permission_classes([AllowAny])
def check_user(request):
    email = request.GET.get("email", "").strip()
    if not email:
        return JsonResponse({"error": "No email provided"}, status=400)

    user_exists = User.objects.filter(email=email).exists()

    return JsonResponse({
        "found": user_exists,
        "avatar_url": "/media/avatars/default.jpg" if not user_exists else "/media/avatars/user_avatar.jpg"
    })
