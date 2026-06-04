from django.contrib import admin
from .models import User, Owner, House, Fee, Repair, Complaint, Visitor, Notice


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'name', 'role', 'phone', 'created_at']
    search_fields = ['username', 'name']


@admin.register(Owner)
class OwnerAdmin(admin.ModelAdmin):
    list_display = ['user', 'gender', 'id_card']


@admin.register(House)
class HouseAdmin(admin.ModelAdmin):
    list_display = ['id', 'building', 'unit', 'room', 'area', 'layout', 'status', 'owner']


@admin.register(Fee)
class FeeAdmin(admin.ModelAdmin):
    list_display = ['house', 'amount', 'month', 'status', 'pay_time']


@admin.register(Repair)
class RepairAdmin(admin.ModelAdmin):
    list_display = ['owner', 'content', 'status', 'staff', 'submit_time']


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ['owner', 'content', 'status', 'submit_time']


@admin.register(Visitor)
class VisitorAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'reason', 'house', 'visit_time']


@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ['title', 'publisher', 'publish_time', 'is_public']
