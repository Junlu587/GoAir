from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import Trip
from .forms import TripForm  # 使用 Django Forms


#  显示所有 Trips（列表页面）
def trip_list(request):
    #  获取所有 Trips 并按出发日期降序排列（最新的在最前面）
    trips_list = Trip.objects.filter(user=request.user).all().order_by('-departure_date')

    #  使用 Paginator，每页显示 4 条 Trip 记录
    paginator = Paginator(trips_list, 4)

    #  获取 URL 参数 `?page=2` 这样的页码值
    page_number = request.GET.get('page')

    #  让 `trips` 变量存储当前页的数据
    trips = paginator.get_page(page_number)

    #  渲染 `trip_list.html` 并传递 `trips` 变量
    return render(request, 'trip_list.html', {'trips': trips})


#  显示单个 Trip 详情（详情页面）
def trip_detail(request, trip_id):
    trip = get_object_or_404(Trip, id=trip_id)  # 获取特定 Trip，如果不存在则返回 404
    return render(request, 'trip_detail.html', {'trip': trip})


#  添加新的 Trip（创建）
def add_trip(request):
    if request.method == 'POST':  # 处理提交表单
        form = TripForm(request.POST)
        if form.is_valid():
            trip = form.save(commit=False)
            # 绑定当前登录用户
            trip.user = request.user
            form.save()  # 会自动调用 clean_flight_number，然后保存 origin/departure_date/status
            return redirect('trip_list')  # 保存后跳转到某个列表页
    else:
        form = TripForm()  # 如果是 GET 请求，则创建空表单
    return render(request, 'trip_form.html', {'form': form})


#  编辑已有 Trip（更新）
def edit_trip(request, trip_id):
    trip = get_object_or_404(Trip, id=trip_id)  # 获取特定的 Trip 实例

    if request.method == 'POST':  # 处理表单提交
        form = TripForm(request.POST, instance=trip)
        if form.is_valid():
            form.save()
            # 处理可选字段
            trip.airline_company = request.POST.get('airline_company', '') or None
            trip.seat_number = request.POST.get('seat_number', '') or None
            trip.class_of_service = request.POST.get('class_of_service', '') or None
            trip.save()
            return redirect('trip_detail', trip_id=trip.id)  # 编辑成功后仍然返回详情页
    else:
        form = TripForm(instance=trip)  # 预填充表单数据

    return render(request, 'trip_detail.html', {'trip': trip, 'form': form})


#  删除 Trip（删除）
def delete_trip(request, trip_id):
    trip = get_object_or_404(Trip, id=trip_id)
    # 处理POST请求删除行程
    if request.method == 'POST':
        trip.delete()
        return redirect('trip_list')  # 删除后返回到行程列表页

    return render(request, 'trip_detail.html', {'trip': trip})
