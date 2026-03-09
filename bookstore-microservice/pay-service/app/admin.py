from django.contrib import admin
from .models import Payment, PaymentHistory, Refund


class PaymentHistoryInline(admin.TabularInline):
    model = PaymentHistory
    extra = 0
    readonly_fields = ['created_at']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['transaction_id', 'order_number', 'amount', 'payment_method', 'status', 'created_at']
    list_filter = ['status', 'payment_method']
    search_fields = ['transaction_id', 'order_number']
    readonly_fields = ['transaction_id', 'created_at', 'updated_at']
    inlines = [PaymentHistoryInline]


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    list_display = ['refund_id', 'payment', 'amount', 'status', 'created_at']
    list_filter = ['status']
    search_fields = ['refund_id']
    readonly_fields = ['refund_id', 'created_at']
