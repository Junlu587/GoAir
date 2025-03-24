"""
URL configuration for GoAir project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from allauth.account.views import LoginView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include

from myApp import views
from myApp.external_api.views import ExternalAPIViewSet
from myApp.flights.views import search_flights
from myApp.users.views import check_user
from myApp.views import api_data, help_view, privacy_view, contact_view, modify_info, logout_view, search_view, \
    login_view, signup_view

from myApp.views import home, user_page
from myApp.views import  search_view, book_flight

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('login/', login_view, name='login'),
    path('signup/', signup_view, name='signup'),
    path('logout/', logout_view, name='logout'),
    # path('accounts/google/login/', google_login_view, name='google_login'),
    path('api/auth/login/', LoginView.as_view(), name='api_login'),
    path('api/check_user/', check_user, name='check_user'),

    # 将 externalapi 应用的路由挂载到 /api/external/
    path('api/external/', include('myApp.external_api.urls')),
    path('api/search/', search_flights, name='search'),

    path('accounts/', include('allauth.urls')),  # Django allauth 路由

    path('search/', search_view, name='search'),  # <-- 重点：name='search'

    path('notifications/', include('myApp.notifications.urls')),
    path('alerts/', include('myApp.alerts.urls')),  # 添加 alerts 路由
    path('user/', user_page, name='user_page'),  # 用户管理
    path('modify-info/', modify_info, name='modify_info'),

    path('flights/', include('myApp.flights.urls', 'flights')),  # 航班搜索
    path('trips/', include('myApp.trips.urls')),  # 加入 trips 应用

    path('help/', help_view, name='help'),
    path('privacy/', privacy_view, name='privacy'),
    path('contact/', contact_view, name='contact'),

    path('auth/', include('dj_rest_auth.urls')),
    path('auth/registration/', include('dj_rest_auth.registration.urls')),  # 这里很重要

]

urlpatterns += [
    path('api/data/', api_data, name='api_data'),
]

# 让 Django 在开发模式下能访问 MEDIA 文件
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
