from django.contrib import admin
from .models import Staff, StaffActivity


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'role', 'department', 'is_active_staff', 'created_at']
    list_filter = ['role', 'is_active_staff', 'department']
    search_fields = ['username', 'email', 'phone']


@admin.register(StaffActivity)
class StaffActivityAdmin(admin.ModelAdmin):
    list_display = ['staff', 'action', 'ip_address', 'created_at']
    list_filter = ['action']
    search_fields = ['staff__username', 'description']
