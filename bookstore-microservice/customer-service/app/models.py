from django.db import models
from django.contrib.auth.models import AbstractUser


class Customer(AbstractUser):
    """Customer model extending Django's AbstractUser"""
    phone = models.CharField(max_length=20, blank=True, null=True)
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


class PersonalInfo(models.Model):
    """Personal information model - stores customer's full name details"""
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE, related_name='personal_info')
    fullname = models.CharField(max_length=255)
    nickname = models.CharField(max_length=100, blank=True, null=True)
    gender = models.CharField(max_length=10, choices=[
        ('male', 'Nam'),
        ('female', 'Nữ'),
        ('other', 'Khác')
    ], blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'personal_info'
        verbose_name = 'Personal Information'
        verbose_name_plural = 'Personal Information'

    def __str__(self):
        return f"{self.fullname} ({self.customer.username})"


class JobInfo(models.Model):
    """Job information model - stores customer's career details"""
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE, related_name='job_info')
    job_title = models.CharField(max_length=200)
    company = models.CharField(max_length=300, blank=True, null=True)
    industry = models.CharField(max_length=100, blank=True, null=True)
    years_of_experience = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'job_info'
        verbose_name = 'Job Information'
        verbose_name_plural = 'Job Information'

    def __str__(self):
        return f"{self.job_title} at {self.company or 'N/A'}"


class AddressInfo(models.Model):
    """Address information model - stores customer's address details"""
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE, related_name='address_info')
    street_address = models.CharField(max_length=500)
    ward = models.CharField(max_length=100, blank=True, null=True)
    district = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, default='Vietnam')
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    is_default = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'address_info'
        verbose_name = 'Address Information'
        verbose_name_plural = 'Address Information'

    def __str__(self):
        return f"{self.street_address}, {self.district}, {self.city}"
    
    @property
    def full_address(self):
        """Return formatted full address"""
        parts = [self.street_address]
        if self.ward:
            parts.append(self.ward)
        if self.district:
            parts.append(self.district)
        if self.city:
            parts.append(self.city)
        if self.country and self.country != 'Vietnam':
            parts.append(self.country)
        return ', '.join(parts)


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
