"""应用路由 - 小区物业管理系统"""
from django.urls import path
from . import views

urlpatterns = [
    # ============ 登录/登出 ============
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # ============ 管理员 ============
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    # 用户管理
    path('admin/users/', views.user_list, name='admin_user_list'),
    path('admin/users/create/', views.user_create, name='admin_user_create'),
    path('admin/users/<int:pk>/edit/', views.user_edit, name='admin_user_edit'),
    path('admin/users/<int:pk>/delete/', views.user_delete, name='admin_user_delete'),
    # 数据查看
    path('admin/owners/', views.admin_owner_list, name='admin_owner_list'),
    path('admin/houses/', views.admin_house_list, name='admin_house_list'),
    path('admin/fees/', views.admin_fee_list, name='admin_fee_list'),
    path('admin/repairs/', views.admin_repair_list, name='admin_repair_list'),
    path('admin/complaints/', views.admin_complaint_list, name='admin_complaint_list'),
    path('admin/visitors/', views.admin_visitor_list, name='admin_visitor_list'),
    path('admin/notices/', views.admin_notice_list, name='admin_notice_list'),
    # 统计
    path('admin/statistics/', views.admin_statistics, name='admin_statistics'),

    # ============ 物业员工 ============
    path('staff-dashboard/', views.staff_dashboard, name='staff_dashboard'),
    # 业主管理
    path('staff/owners/', views.staff_owner_list, name='staff_owner_list'),
    path('staff/owners/create/', views.staff_owner_create, name='staff_owner_create'),
    path('staff/owners/<int:pk>/edit/', views.staff_owner_edit, name='staff_owner_edit'),
    path('staff/owners/<int:pk>/delete/', views.staff_owner_delete, name='staff_owner_delete'),
    # 房屋管理
    path('staff/houses/', views.staff_house_list, name='staff_house_list'),
    path('staff/houses/create/', views.staff_house_create, name='staff_house_create'),
    path('staff/houses/<int:pk>/edit/', views.staff_house_edit, name='staff_house_edit'),
    path('staff/houses/<int:pk>/delete/', views.staff_house_delete, name='staff_house_delete'),
    # 物业费管理
    path('staff/fees/', views.staff_fee_list, name='staff_fee_list'),
    path('staff/fees/create/', views.staff_fee_create, name='staff_fee_create'),
    path('staff/fees/<int:pk>/pay/', views.staff_fee_pay, name='staff_fee_pay'),
    path('staff/fees/<int:pk>/delete/', views.staff_fee_delete, name='staff_fee_delete'),
    # 报修管理
    path('staff/repairs/', views.staff_repair_list, name='staff_repair_list'),
    path('staff/repairs/<int:pk>/process/', views.staff_repair_process, name='staff_repair_process'),
    # 访客管理
    path('staff/visitors/', views.staff_visitor_list, name='staff_visitor_list'),
    path('staff/visitors/create/', views.staff_visitor_create, name='staff_visitor_create'),
    path('staff/visitors/<int:pk>/delete/', views.staff_visitor_delete, name='staff_visitor_delete'),
    # 投诉管理
    path('staff/complaints/', views.staff_complaint_list, name='staff_complaint_list'),
    path('staff/complaints/<int:pk>/reply/', views.staff_complaint_reply, name='staff_complaint_reply'),
    # 公告管理
    path('staff/notices/', views.staff_notice_list, name='staff_notice_list'),
    path('staff/notices/create/', views.staff_notice_create, name='staff_notice_create'),
    path('staff/notices/<int:pk>/edit/', views.staff_notice_edit, name='staff_notice_edit'),
    path('staff/notices/<int:pk>/delete/', views.staff_notice_delete, name='staff_notice_delete'),
    # 统计
    path('staff/statistics/', views.staff_statistics, name='staff_statistics'),

    # ============ 业主 ============
    path('owner-dashboard/', views.owner_dashboard, name='owner_dashboard'),
    path('owner/profile/', views.owner_profile, name='owner_profile'),
    path('owner/fees/', views.owner_fee_list, name='owner_fee_list'),
    path('owner/repairs/', views.owner_repair_list, name='owner_repair_list'),
    path('owner/repairs/create/', views.owner_repair_create, name='owner_repair_create'),
    path('owner/complaints/', views.owner_complaint_list, name='owner_complaint_list'),
    path('owner/complaints/create/', views.owner_complaint_create, name='owner_complaint_create'),
    path('owner/notices/', views.owner_notice_list, name='owner_notice_list'),
]
