from django.db import models
import uuid


class Payment(models.Model):
    """Thanh toán"""
    STATUS_CHOICES = [
        ('pending', 'Chờ thanh toán'),
        ('processing', 'Đang xử lý'),
        ('completed', 'Đã thanh toán'),
        ('failed', 'Thất bại'),
        ('refunded', 'Đã hoàn tiền'),
        ('cancelled', 'Đã hủy'),
    ]

    METHOD_CHOICES = [
        ('cod', 'Thanh toán khi nhận hàng'),
        ('bank_transfer', 'Chuyển khoản ngân hàng'),
        ('credit_card', 'Thẻ tín dụng'),
        ('momo', 'Ví MoMo'),
        ('zalopay', 'ZaloPay'),
        ('vnpay', 'VNPay'),
    ]

    transaction_id = models.CharField(max_length=50, unique=True, editable=False)
    order_id = models.IntegerField()
    order_number = models.CharField(max_length=50)
    customer_id = models.IntegerField()
    
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=METHOD_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Payment details
    bank_code = models.CharField(max_length=20, blank=True, null=True)
    card_number = models.CharField(max_length=20, blank=True, null=True)  # Last 4 digits only
    payment_gateway_response = models.JSONField(blank=True, null=True)
    
    paid_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'payments'
        ordering = ['-created_at']

    def __str__(self):
        return f"Payment {self.transaction_id} - {self.order_number}"

    def save(self, *args, **kwargs):
        if not self.transaction_id:
            self.transaction_id = f"PAY-{uuid.uuid4().hex[:10].upper()}"
        super().save(*args, **kwargs)


class PaymentHistory(models.Model):
    """Lịch sử thanh toán"""
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='history')
    status = models.CharField(max_length=20)
    note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'payment_history'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.payment.transaction_id} - {self.status}"


class Refund(models.Model):
    """Hoàn tiền"""
    STATUS_CHOICES = [
        ('pending', 'Chờ xử lý'),
        ('processing', 'Đang xử lý'),
        ('completed', 'Đã hoàn tiền'),
        ('rejected', 'Từ chối'),
    ]

    refund_id = models.CharField(max_length=50, unique=True, editable=False)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='refunds')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    processed_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'refunds'
        ordering = ['-created_at']

    def __str__(self):
        return f"Refund {self.refund_id}"

    def save(self, *args, **kwargs):
        if not self.refund_id:
            self.refund_id = f"REF-{uuid.uuid4().hex[:10].upper()}"
        super().save(*args, **kwargs)
