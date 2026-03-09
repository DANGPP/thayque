from django.contrib import admin
from .models import Customer, CustomerProfile


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'phone', 'is_active_customer', 'created_at']
    list_filter = ['is_active_customer', 'created_at']
    search_fields = ['username', 'email', 'phone']
    ordering = ['-created_at']


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ['customer', 'loyalty_points', 'total_orders', 'total_spent']
    search_fields = ['customer__username', 'customer__email']
