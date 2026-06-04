"""
视图函数 - 小区物业管理系统
包含: 登录认证、管理员功能、物业员工功能、业主功能、原生SQL调用
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import connection
from django.utils import timezone
from datetime import datetime
from functools import wraps
from .models import User, Owner, House, Fee, Repair, Complaint, Visitor, Notice
from .forms import (
    LoginForm, UserForm, OwnerForm, HouseForm, FeeForm,
    RepairForm, RepairProcessForm, ComplaintForm, ComplaintReplyForm,
    VisitorForm, NoticeForm, ProfileForm
)


# ==================== 登录认证装饰器 ====================
def login_required(view_func):
    """登录检查装饰器"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('user_id'):
            messages.warning(request, '请先登录')
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


def role_required(*roles):
    """角色权限检查装饰器"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            user_role = request.session.get('user_role')
            if user_role not in roles:
                messages.error(request, '无权访问该页面')
                return redirect(f'{user_role}_dashboard')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


# ==================== 登录/登出 ====================
def login_view(request):
    """统一登录页面"""
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            role = form.cleaned_data['role']
            try:
                user = User.objects.get(username=username, role=role)
                if user.check_password(password):
                    request.session['user_id'] = user.id
                    request.session['user_name'] = user.name
                    request.session['user_role'] = user.role
                    messages.success(request, f'欢迎回来，{user.name}！')
                    return redirect(f'{role}_dashboard')
                else:
                    messages.error(request, '密码错误')
            except User.DoesNotExist:
                messages.error(request, '用户不存在或角色不匹配')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    """登出"""
    request.session.flush()
    messages.success(request, '已安全退出')
    return redirect('login')


# ==================== 管理员视图 ====================
@login_required
@role_required('admin')
def admin_dashboard(request):
    """管理员主页：数据概览"""
    ctx = {
        'owner_count': Owner.objects.count(),
        'house_count': House.objects.count(),
        'fee_count': Fee.objects.count(),
        'repair_count': Repair.objects.count(),
        'complaint_count': Complaint.objects.count(),
        'staff_count': User.objects.filter(role='staff').count(),
    }
    return render(request, 'admin/dashboard.html', ctx)


# --- 用户管理 ---
@login_required
@role_required('admin')
def user_list(request):
    """管理员-用户列表"""
    users = User.objects.all().order_by('-created_at')
    return render(request, 'admin/user_list.html', {'users': users})


@login_required
@role_required('admin')
def user_create(request):
    """管理员-创建用户"""
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            # 如果创建的是业主，同时创建业主详情记录
            if user.role == 'owner':
                Owner.objects.create(user=user)
            messages.success(request, f'用户 {user.name} 创建成功')
            return redirect('admin_user_list')
    else:
        form = UserForm()
    return render(request, 'admin/user_form.html', {'form': form, 'action': '创建'})


@login_required
@role_required('admin')
def user_edit(request, pk):
    """管理员-编辑用户"""
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            user = form.save(commit=False)
            new_password = form.cleaned_data.get('password')
            if new_password:
                user.set_password(new_password)
            user.save()
            messages.success(request, '用户信息更新成功')
            return redirect('admin_user_list')
    else:
        form = UserForm(instance=user)
        form.fields.pop('confirm_password', None)
    return render(request, 'admin/user_form.html', {'form': form, 'action': '编辑', 'user': user})


@login_required
@role_required('admin')
def user_delete(request, pk):
    """管理员-删除用户"""
    user = get_object_or_404(User, pk=pk)
    if user.role == 'admin':
        messages.error(request, '不能删除管理员账号')
    else:
        user.delete()
        messages.success(request, '用户已删除')
    return redirect('admin_user_list')


# --- 通用数据管理（管理员查看所有数据） ---
@login_required
@role_required('admin')
def admin_owner_list(request):
    return render(request, 'admin/owner_list.html', {
        'owners': Owner.objects.select_related('user').all()
    })


@login_required
@role_required('admin')
def admin_house_list(request):
    return render(request, 'admin/house_list.html', {
        'houses': House.objects.select_related('owner__user').all()
    })


@login_required
@role_required('admin')
def admin_fee_list(request):
    return render(request, 'admin/fee_list.html', {
        'fees': Fee.objects.select_related('house').all().order_by('-month')
    })


@login_required
@role_required('admin')
def admin_repair_list(request):
    return render(request, 'admin/repair_list.html', {
        'repairs': Repair.objects.select_related('owner__user', 'staff', 'house').all().order_by('-submit_time')
    })


@login_required
@role_required('admin')
def admin_complaint_list(request):
    return render(request, 'admin/complaint_list.html', {
        'complaints': Complaint.objects.select_related('owner__user').all().order_by('-submit_time')
    })


@login_required
@role_required('admin')
def admin_visitor_list(request):
    return render(request, 'admin/visitor_list.html', {
        'visitors': Visitor.objects.select_related('house', 'staff').all().order_by('-visit_time')
    })


@login_required
@role_required('admin')
def admin_notice_list(request):
    return render(request, 'admin/notice_list.html', {
        'notices': Notice.objects.select_related('publisher').all().order_by('-publish_time')
    })


@login_required
@role_required('admin')
def admin_statistics(request):
    """管理员-统计报表（调用存储过程）"""
    fee_stats = None
    repair_stats = None
    fee_month = request.GET.get('fee_month', datetime.now().strftime('%Y-%m'))
    repair_start = request.GET.get('repair_start', f'{datetime.now().year}-01-01')
    repair_end = request.GET.get('repair_end', datetime.now().strftime('%Y-%m-%d'))

    # 调用存储过程 fee_stat
    with connection.cursor() as cursor:
        cursor.callproc('fee_stat', [fee_month])
        fee_stats = cursor.fetchall()  # 返回一行统计数据

    # 调用存储过程 repair_stat
    with connection.cursor() as cursor:
        cursor.callproc('repair_stat', [repair_start, repair_end])
        repair_stats = cursor.fetchall()  # 返回多行各状态统计

    # 查询欠费视图
    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM view_owe_fee')
        owe_columns = [col[0] for col in cursor.description]
        owe_list = [dict(zip(owe_columns, row)) for row in cursor.fetchall()]

    # 查询报修进度视图
    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM view_repair_progress')
        repair_columns = [col[0] for col in cursor.description]
        repair_progress = [dict(zip(repair_columns, row)) for row in cursor.fetchall()]

    return render(request, 'admin/statistics.html', {
        'fee_stats': fee_stats,
        'repair_stats': repair_stats,
        'owe_list': owe_list,
        'repair_progress': repair_progress,
        'fee_month': fee_month,
        'repair_start': repair_start,
        'repair_end': repair_end,
    })


# ==================== 物业员工视图 ====================
@login_required
@role_required('staff')
def staff_dashboard(request):
    """员工主页"""
    ctx = {
        'owner_count': Owner.objects.count(),
        'house_count': House.objects.count(),
        'pending_repair': Repair.objects.filter(status=0).count(),
        'pending_complaint': Complaint.objects.filter(status=0).count(),
    }
    return render(request, 'staff/dashboard.html', ctx)


# --- 员工-业主管理 ---
@login_required
@role_required('staff')
def staff_owner_list(request):
    owners = Owner.objects.select_related('user').all()
    return render(request, 'staff/owner_list.html', {'owners': owners})


@login_required
@role_required('staff')
def staff_owner_create(request):
    """员工-创建业主（同时创建 User + Owner）"""
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        owner_form = OwnerForm(request.POST)
        if user_form.is_valid() and owner_form.is_valid():
            user = user_form.save(commit=False)
            user.role = 'owner'
            user.set_password(user_form.cleaned_data['password'])
            user.save()
            owner = owner_form.save(commit=False)
            owner.user = user
            owner.save()
            messages.success(request, f'业主 {user.name} 创建成功')
            return redirect('staff_owner_list')
    else:
        user_form = UserForm(initial={'role': 'owner'})
        owner_form = OwnerForm()
    return render(request, 'staff/owner_form.html', {
        'user_form': user_form, 'owner_form': owner_form, 'action': '创建'
    })


@login_required
@role_required('staff')
def staff_owner_edit(request, pk):
    """员工-编辑业主信息"""
    owner = get_object_or_404(Owner, pk=pk)
    if request.method == 'POST':
        owner_form = OwnerForm(request.POST, instance=owner)
        if owner_form.is_valid():
            owner_form.save()
            messages.success(request, '业主信息更新成功')
            return redirect('staff_owner_list')
    else:
        owner_form = OwnerForm(instance=owner)
    return render(request, 'staff/owner_form.html', {
        'owner_form': owner_form, 'owner': owner, 'action': '编辑'
    })


@login_required
@role_required('staff')
def staff_owner_delete(request, pk):
    owner = get_object_or_404(Owner, pk=pk)
    user = owner.user
    owner.delete()
    user.delete()
    messages.success(request, '业主已删除')
    return redirect('staff_owner_list')


# --- 员工-房屋管理 ---
@login_required
@role_required('staff')
def staff_house_list(request):
    houses = House.objects.select_related('owner__user').all()
    return render(request, 'staff/house_list.html', {'houses': houses})


@login_required
@role_required('staff')
def staff_house_create(request):
    if request.method == 'POST':
        form = HouseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '房屋添加成功')
            return redirect('staff_house_list')
    else:
        form = HouseForm()
    return render(request, 'staff/house_form.html', {'form': form, 'action': '添加'})


@login_required
@role_required('staff')
def staff_house_edit(request, pk):
    house = get_object_or_404(House, pk=pk)
    if request.method == 'POST':
        form = HouseForm(request.POST, instance=house)
        if form.is_valid():
            form.save()
            messages.success(request, '房屋信息更新成功')
            return redirect('staff_house_list')
    else:
        form = HouseForm(instance=house)
    return render(request, 'staff/house_form.html', {'form': form, 'action': '编辑', 'house': house})


@login_required
@role_required('staff')
def staff_house_delete(request, pk):
    house = get_object_or_404(House, pk=pk)
    house.delete()
    messages.success(request, '房屋已删除')
    return redirect('staff_house_list')


# --- 员工-物业费管理 ---
@login_required
@role_required('staff')
def staff_fee_list(request):
    fees = Fee.objects.select_related('house').all().order_by('-month', 'house__building')
    return render(request, 'staff/fee_list.html', {'fees': fees})


@login_required
@role_required('staff')
def staff_fee_create(request):
    """员工-生成物业费账单"""
    if request.method == 'POST':
        form = FeeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '物业费账单生成成功')
            return redirect('staff_fee_list')
    else:
        form = FeeForm()
    return render(request, 'staff/fee_form.html', {'form': form, 'action': '生成'})


@login_required
@role_required('staff')
def staff_fee_pay(request, pk):
    """员工-标记缴费（将 status 改为 1，记录缴费时间）"""
    fee = get_object_or_404(Fee, pk=pk)
    if fee.status == 1:
        messages.warning(request, '该账单已缴费')
    else:
        fee.status = 1
        fee.pay_time = timezone.now()
        fee.save()
        messages.success(request, '缴费标记成功')
    return redirect('staff_fee_list')


@login_required
@role_required('staff')
def staff_fee_delete(request, pk):
    fee = get_object_or_404(Fee, pk=pk)
    fee.delete()
    messages.success(request, '账单已删除')
    return redirect('staff_fee_list')


# --- 员工-报修管理 ---
@login_required
@role_required('staff')
def staff_repair_list(request):
    repairs = Repair.objects.select_related('owner__user', 'staff', 'house').all().order_by('-submit_time')
    return render(request, 'staff/repair_list.html', {'repairs': repairs})


@login_required
@role_required('staff')
def staff_repair_process(request, pk):
    """员工-处理报修（更新状态、分配员工、填写结果）"""
    repair = get_object_or_404(Repair, pk=pk)
    if request.method == 'POST':
        form = RepairProcessForm(request.POST, instance=repair)
        if form.is_valid():
            repair = form.save()
            messages.success(request, '报修处理成功')
            return redirect('staff_repair_list')
    else:
        form = RepairProcessForm(instance=repair)
    staff_list = User.objects.filter(role='staff')
    return render(request, 'staff/repair_form.html', {
        'form': form, 'repair': repair, 'staff_list': staff_list
    })


# --- 员工-访客管理 ---
@login_required
@role_required('staff')
def staff_visitor_list(request):
    visitors = Visitor.objects.select_related('house', 'staff').all().order_by('-visit_time')
    return render(request, 'staff/visitor_list.html', {'visitors': visitors})


@login_required
@role_required('staff')
def staff_visitor_create(request):
    if request.method == 'POST':
        form = VisitorForm(request.POST)
        if form.is_valid():
            visitor = form.save(commit=False)
            user_id = request.session.get('user_id')
            visitor.staff = User.objects.get(pk=user_id)
            visitor.save()
            messages.success(request, '访客登记成功')
            return redirect('staff_visitor_list')
    else:
        form = VisitorForm()
    return render(request, 'staff/visitor_form.html', {'form': form, 'action': '登记'})


@login_required
@role_required('staff')
def staff_visitor_delete(request, pk):
    visitor = get_object_or_404(Visitor, pk=pk)
    visitor.delete()
    messages.success(request, '访客记录已删除')
    return redirect('staff_visitor_list')


# --- 员工-投诉管理 ---
@login_required
@role_required('staff')
def staff_complaint_list(request):
    complaints = Complaint.objects.select_related('owner__user').all().order_by('-submit_time')
    return render(request, 'staff/complaint_list.html', {'complaints': complaints})


@login_required
@role_required('staff')
def staff_complaint_reply(request, pk):
    """员工-回复投诉"""
    complaint = get_object_or_404(Complaint, pk=pk)
    if request.method == 'POST':
        form = ComplaintReplyForm(request.POST, instance=complaint)
        if form.is_valid():
            complaint = form.save()
            complaint.status = 1
            complaint.reply_time = timezone.now()
            complaint.save()
            messages.success(request, '投诉已回复')
            return redirect('staff_complaint_list')
    else:
        form = ComplaintReplyForm(instance=complaint)
    return render(request, 'staff/complaint_form.html', {
        'form': form, 'complaint': complaint
    })


# --- 员工-公告管理 ---
@login_required
@role_required('staff')
def staff_notice_list(request):
    notices = Notice.objects.select_related('publisher').all().order_by('-publish_time')
    return render(request, 'staff/notice_list.html', {'notices': notices})


@login_required
@role_required('staff')
def staff_notice_create(request):
    if request.method == 'POST':
        form = NoticeForm(request.POST)
        if form.is_valid():
            notice = form.save(commit=False)
            notice.publisher = User.objects.get(pk=request.session.get('user_id'))
            notice.save()
            messages.success(request, '公告发布成功')
            return redirect('staff_notice_list')
    else:
        form = NoticeForm()
    return render(request, 'staff/notice_form.html', {'form': form, 'action': '发布'})


@login_required
@role_required('staff')
def staff_notice_edit(request, pk):
    notice = get_object_or_404(Notice, pk=pk)
    if request.method == 'POST':
        form = NoticeForm(request.POST, instance=notice)
        if form.is_valid():
            form.save()
            messages.success(request, '公告更新成功')
            return redirect('staff_notice_list')
    else:
        form = NoticeForm(instance=notice)
    return render(request, 'staff/notice_form.html', {'form': form, 'action': '编辑', 'notice': notice})


@login_required
@role_required('staff')
def staff_notice_delete(request, pk):
    notice = get_object_or_404(Notice, pk=pk)
    notice.delete()
    messages.success(request, '公告已删除')
    return redirect('staff_notice_list')


# --- 员工-统计报表 ---
@login_required
@role_required('staff')
def staff_statistics(request):
    """员工-统计报表（与管理员相同）"""
    fee_month = request.GET.get('fee_month', datetime.now().strftime('%Y-%m'))
    repair_start = request.GET.get('repair_start', f'{datetime.now().year}-01-01')
    repair_end = request.GET.get('repair_end', datetime.now().strftime('%Y-%m-%d'))

    with connection.cursor() as cursor:
        cursor.callproc('fee_stat', [fee_month])
        fee_stats = cursor.fetchall()

    with connection.cursor() as cursor:
        cursor.callproc('repair_stat', [repair_start, repair_end])
        repair_stats = cursor.fetchall()

    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM view_owe_fee')
        owe_columns = [col[0] for col in cursor.description]
        owe_list = [dict(zip(owe_columns, row)) for row in cursor.fetchall()]

    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM view_repair_progress')
        rp_columns = [col[0] for col in cursor.description]
        repair_progress = [dict(zip(rp_columns, row)) for row in cursor.fetchall()]

    return render(request, 'staff/statistics.html', {
        'fee_stats': fee_stats, 'repair_stats': repair_stats,
        'owe_list': owe_list, 'repair_progress': repair_progress,
        'fee_month': fee_month, 'repair_start': repair_start, 'repair_end': repair_end,
    })


# ==================== 业主视图 ====================
def get_owner_from_session(request):
    """从 session 获取当前业主对象"""
    user_id = request.session.get('user_id')
    if user_id:
        try:
            return Owner.objects.get(user_id=user_id)
        except Owner.DoesNotExist:
            return None
    return None


@login_required
@role_required('owner')
def owner_dashboard(request):
    """业主主页"""
    owner = get_owner_from_session(request)
    if not owner:
        messages.error(request, '业主信息异常')
        return redirect('login')
    house = House.objects.filter(owner=owner).first()
    unpaid = Fee.objects.filter(house__owner=owner, status=0).count()
    ctx = {
        'owner': owner,
        'house': house,
        'unpaid_count': unpaid,
        'repair_count': Repair.objects.filter(owner=owner).count(),
    }
    return render(request, 'owner/dashboard.html', ctx)


@login_required
@role_required('owner')
def owner_profile(request):
    """业主-查看/修改个人信息"""
    owner = get_owner_from_session(request)
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=owner)
        phone = request.POST.get('phone', '')
        if form.is_valid():
            form.save()
            owner.user.phone = phone
            owner.user.save()
            messages.success(request, '个人信息更新成功')
            return redirect('owner_profile')
    else:
        form = ProfileForm(instance=owner)
    return render(request, 'owner/profile.html', {'form': form, 'owner': owner})


@login_required
@role_required('owner')
def owner_fee_list(request):
    """业主-查看物业费账单"""
    owner = get_owner_from_session(request)
    fees = Fee.objects.select_related('house').filter(
        house__owner=owner
    ).order_by('-month')
    return render(request, 'owner/fee_list.html', {'fees': fees})


@login_required
@role_required('owner')
def owner_repair_list(request):
    """业主-报修列表"""
    owner = get_owner_from_session(request)
    repairs = Repair.objects.select_related('house', 'staff').filter(
        owner=owner
    ).order_by('-submit_time')
    return render(request, 'owner/repair_list.html', {'repairs': repairs})


@login_required
@role_required('owner')
def owner_repair_create(request):
    """业主-提交报修"""
    owner = get_owner_from_session(request)
    if request.method == 'POST':
        form = RepairForm(request.POST)
        # 限制房屋选择为业主自己的房屋
        form.fields['house'].queryset = House.objects.filter(owner=owner)
        if form.is_valid():
            repair = form.save(commit=False)
            repair.owner = owner
            repair.save()
            messages.success(request, '报修提交成功，请等待处理')
            return redirect('owner_repair_list')
    else:
        form = RepairForm()
        form.fields['house'].queryset = House.objects.filter(owner=owner)
    return render(request, 'owner/repair_form.html', {'form': form})


@login_required
@role_required('owner')
def owner_complaint_list(request):
    """业主-投诉建议列表"""
    owner = get_owner_from_session(request)
    complaints = Complaint.objects.filter(owner=owner).order_by('-submit_time')
    return render(request, 'owner/complaint_list.html', {'complaints': complaints})


@login_required
@role_required('owner')
def owner_complaint_create(request):
    """业主-提交投诉建议"""
    owner = get_owner_from_session(request)
    if request.method == 'POST':
        form = ComplaintForm(request.POST)
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.owner = owner
            complaint.save()
            messages.success(request, '投诉/建议提交成功')
            return redirect('owner_complaint_list')
    else:
        form = ComplaintForm()
    return render(request, 'owner/complaint_form.html', {'form': form})


@login_required
@role_required('owner')
def owner_notice_list(request):
    """业主-查看公告（仅公开的）"""
    notices = Notice.objects.select_related('publisher').filter(
        is_public=True
    ).order_by('-publish_time')
    return render(request, 'owner/notice_list.html', {'notices': notices})
