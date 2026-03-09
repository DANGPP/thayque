from django.db import models
from django.contrib.auth.models import AbstractUser


class Customer(AbstractUser):
    """Customer model extending Django's AbstractUser"""
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    avatar = models.URLField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    is_active_customer = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'customers'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.username} - {self.email}"


class CustomerProfile(models.Model):
    """Extended profile for customer"""
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE, related_name='profile')
    loyalty_points = models.IntegerField(default=0)
    total_orders = models.IntegerField(default=0)
    total_spent = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    preferred_payment_method = models.CharField(max_length=50, blank=True, null=True)
    preferred_shipping_address = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'customer_profiles'

    def __str__(self):
        return f"Profile of {self.customer.username}"
