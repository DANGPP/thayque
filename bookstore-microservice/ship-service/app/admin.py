from django.contrib import admin
from .models import Shipment, ShipmentTracking


class ShipmentTrackingInline(admin.TabularInline):
    model = ShipmentTracking
    extra = 0
    readonly_fields = ['created_at']


@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ['tracking_number', 'order_number', 'customer_name', 'status', 'shipping_method', 'created_at']
    list_filter = ['status', 'shipping_method']
    search_fields = ['tracking_number', 'order_number', 'customer_name', 'customer_phone']
    readonly_fields = ['tracking_number', 'created_at', 'updated_at']
    inlines = [ShipmentTrackingInline]
    list_editable = ['status']
