from django.contrib import admin
from .models import Customer, CustomerProfile, PersonalInfo, JobInfo, AddressInfo


class PersonalInfoInline(admin.StackedInline):
    model = PersonalInfo
    extra = 0
    can_delete = False


class JobInfoInline(admin.StackedInline):
    model = JobInfo
    extra = 0
    can_delete = False


class AddressInfoInline(admin.StackedInline):
    model = AddressInfo
    extra = 0
    can_delete = False


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'phone', 'is_active_customer', 'created_at']
    list_filter = ['is_active_customer', 'created_at']
    search_fields = ['username', 'email', 'phone']
    ordering = ['-created_at']
    inlines = [PersonalInfoInline, JobInfoInline, AddressInfoInline]


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ['customer', 'loyalty_points', 'total_orders', 'total_spent']
    search_fields = ['customer__username', 'customer__email']


@admin.register(PersonalInfo)
class PersonalInfoAdmin(admin.ModelAdmin):
    list_display = ['customer', 'fullname', 'gender', 'created_at']
    search_fields = ['customer__username', 'fullname']
    list_filter = ['gender']


@admin.register(JobInfo)
class JobInfoAdmin(admin.ModelAdmin):
    list_display = ['customer', 'job_title', 'company', 'industry', 'created_at']
    search_fields = ['customer__username', 'job_title', 'company']
    list_filter = ['industry']


@admin.register(AddressInfo)
class AddressInfoAdmin(admin.ModelAdmin):
    list_display = ['customer', 'city', 'district', 'is_default', 'created_at']
    search_fields = ['customer__username', 'street_address', 'city']
    list_filter = ['city', 'is_default']
