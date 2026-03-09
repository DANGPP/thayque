from django.db import models
import uuid


class Shipment(models.Model):
    """Vận chuyển"""
    STATUS_CHOICES = [
        ('pending', 'Chờ xử lý'),
        ('picked_up', 'Đã lấy hàng'),
        ('in_transit', 'Đang vận chuyển'),
        ('out_for_delivery', 'Đang giao'),
        ('delivered', 'Đã giao'),
        ('failed', 'Giao thất bại'),
        ('returned', 'Đã trả lại'),
    ]

    METHOD_CHOICES = [
        ('standard', 'Giao hàng tiêu chuẩn (3-5 ngày)'),
        ('express', 'Giao hàng nhanh (1-2 ngày)'),
        ('same_day', 'Giao trong ngày'),
    ]

    tracking_number = models.CharField(max_length=50, unique=True, editable=False)
    order_id = models.IntegerField()
    order_number = models.CharField(max_length=50)
    
    # Receiver info
    customer_name = models.CharField(max_length=255)
    customer_phone = models.CharField(max_length=20)
    shipping_address = models.TextField()
    
    shipping_method = models.CharField(max_length=20, choices=METHOD_CHOICES, default='standard')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Carrier info
    carrier = models.CharField(max_length=100, default='BookStore Express')
    estimated_delivery = models.DateField(blank=True, null=True)
    
    notes = models.TextField(blank=True, null=True)
    delivered_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'shipments'
        ordering = ['-created_at']

    def __str__(self):
        return f"Shipment {self.tracking_number}"

    def save(self, *args, **kwargs):
        if not self.tracking_number:
            self.tracking_number = f"SHIP-{uuid.uuid4().hex[:10].upper()}"
        super().save(*args, **kwargs)


class ShipmentTracking(models.Model):
    """Theo dõi vận chuyển"""
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name='tracking_history')
    status = models.CharField(max_length=20)
    location = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'shipment_tracking'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.shipment.tracking_number} - {self.status}"
