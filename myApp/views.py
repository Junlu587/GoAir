import json

import requests
from allauth.account.views import login
from allauth.socialaccount.forms import SignupForm
from django.contrib import messages
from django.contrib.auth import logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.middleware.csrf import get_token
from django.shortcuts import render, redirect
from django.http import JsonResponse, request
from django.views.decorators.csrf import csrf_exempt
from rest_framework.reverse import reverse

from GoAir import settings
from myApp.alerts.models import Alert
from myApp.external_api.views import ExternalAPIViewSet
from myApp.flights.models import Flight
from myApp.notifications.models import Notification
from myApp.trips.models import Trip
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
@method_decorator(csrf_exempt, name='dispatch')
class ExternalAPIViewSet(viewsets.ViewSet):

# 主页
    def home(request):
        if request.user.is_authenticated:
            trips = Trip.objects.filter(user=request.user).order_by('-departure_date')
            alerts = Alert.objects.filter(user=request.user).order_by('-departure_date')
            notifications = Notification.objects.filter(user=request.user).order_by('-flight__departure_date')
        else:
            trips = []
            alerts = []
            notifications = []

        return render(request, 'home.html', {
        'trips': trips,
        'alerts': alerts,
        'notifications': notifications,
        'media_url': settings.MEDIA_URL
    })


# 登录页面
@csrf_exempt
def login_view(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)  # 解析 JSON 数据
            email = data.get("login")  # 确保和前端 fetch 里的 key 对应
            password = data.get("password")

            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                return JsonResponse({"message": "Login successful", "status": "ok"})
            else:
                return JsonResponse({"message": "Invalid credentials", "status": "error"}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON", "status": "error"}, status=400)

    return render(request, 'account/login.html', {
        'media_url': settings.MEDIA_URL,
        'csrf_token': get_token(request)
    })


# 注册页面
def signup_view(request):
    return render(request, 'account/signup.html', {  # 添加 request 作为第一个参数，并确保模板名称正确
        'media_url': settings.MEDIA_URL
    })


# def google_login_view(request):
#     """
#     一个自定义视图，用于渲染你自定义的 Google 登录页面。
#     注意：这和 allauth 内部处理流程有些不同，通常 allauth
#     会直接处理 /accounts/google/login/ 路径。
#     如果你想自己控制页面，可以这样写。
#     """
#     form = SignupForm()
#     # ...
#
#     return render(
#         request,
#         "socialaccount/providers/google/login.html",
#         {
#             "form": form,
#             "action_url": reverse("socialaccount_login", args=["google"]) + "?process=login",
#         }
#     )


# 航班搜索页面
def search_view(request):
    # api_url = request.build_absolute_uri(reverse("flight_search"))
    # response = requests.get(api_url, params=request.GET)  # 直接向 API 发送请求
    # flights = response.json()
    # # 调试信息
    # # print(f"API URL: {api_url}")  # 打印 API 请求地址
    # # print(f"Response Status Code: {response.status_code}")  # 打印 API 响应状态码
    # # print(f"Flights Data: {flights}")  # 打印 API 返回的数据
    #
    # if response.status_code != 200:
    #     return render(request, "search.html", {"flights": [], "error": "API 请求失败"})
    #
    # # 3. 确保数据结构正确
    # flights_list = flights if isinstance(flights, list) else []
    #
    # paginator = Paginator(flights_list, 6)
    # page_number = request.GET.get("page", 1)
    # page_obj = paginator.get_page(page_number)
    # # print(f"API 响应状态码: {response.status_code}")
    # # print(f"API 返回的原始数据: {flights}")
    # return render(request, "search.html", {"flights": page_obj})
    origin = request.GET.get("origin", "")
    destination = request.GET.get("destination", "")
    date = request.GET.get("date", "")

    flights = Flight.objects.filter(origin=origin, destination=destination, departure_date=date)

    return render(request, "search.html", {"flights": flights})

# 机票预订页面
def book_flight(request):
    return render(request, "trip_list.html")


# 用户界面
@login_required
def user_page(request):
    # 通过 context 把当前用户对象 user 传递给模板
    return render(request, 'user.html', {
        'user': request.user
    })


@login_required
def modify_info(request):
    """
    处理用户修改信息的逻辑：用户名、邮箱、电话、头像
    POST 提交后更新数据库并重定向到 user_page
    """
    if request.method == 'POST':
        new_username = request.POST.get('username')
        new_email = request.POST.get('email')
        new_phone = request.POST.get('phone')
        new_avatar = request.FILES.get('avatar')  # 通过 FILES 获取上传的头像文件

        user = request.user
        # 如果前端提交了 username/email/phone，就更新，否则保持为空或原值
        user.username = new_username or ''
        user.email = new_email or ''
        user.phone = new_phone or ''

        if new_avatar:
            # 如果上传了新的头像文件，则更新
            user.avatar = new_avatar

        user.save()
        # 修改信息后重定向到 user_page
        return redirect('user_page')
    # 若不是 POST 请求，直接跳转到 user_page
    return redirect('user_page')


def logout_view(request):
    """
    退出登录并返回 user_page (也可改为返回首页)
    """
    logout(request)
    return redirect('home')


@login_required
# 价格提醒页面
def notifications(request):
    return render(request, "notifications.html")


def api_data(request):
    data = {"message": "Hello from Django API!"}
    return JsonResponse(data)


@login_required(login_url='/login/')  # 未登录用户跳转到 login 页面
def trip_list(request):
    user = request.user
    trips = Trip.objects.filter(user=user).order_by('-departure_date')  # 假设 Trip 关联 user
    return render(request, 'trip_list.html')  # 确保你有 trips.html 模板


def help_view(request):
    return render(request, 'help.html')


def privacy_view(request):
    return render(request, 'privacy.html')


def contact_view(request):
    return render(request, 'contactus.html')
