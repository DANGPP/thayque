from django.db import models
from django.contrib.auth.models import AbstractUser


class Staff(AbstractUser):
    """Nhân viên"""
    ROLE_CHOICES = [
        ('admin', 'Quản trị viên'),
        ('manager', 'Quản lý'),
        ('staff', 'Nhân viên'),
        ('warehouse', 'Kho'),
        ('shipper', 'Giao hàng'),
    ]

    phone = models.CharField(max_length=20, blank=True, null=True)
    avatar = models.URLField(blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='staff')
    department = models.CharField(max_length=100, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    hire_date = models.DateField(blank=True, null=True)
    salary = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    
    is_active_staff = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'staff'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.username} - {self.get_role_display()}"


class StaffActivity(models.Model):
    """Lịch sử hoạt động của nhân viên"""
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='activities')
    action = models.CharField(max_length=100)
    description = models.TextField()
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'staff_activities'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.staff.username} - {self.action}"
