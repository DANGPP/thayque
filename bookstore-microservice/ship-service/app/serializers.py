from rest_framework import serializers
from .models import Shipment, ShipmentTracking


class ShipmentTrackingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShipmentTracking
        fields = '__all__'


class ShipmentSerializer(serializers.ModelSerializer):
    tracking_history = ShipmentTrackingSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    method_display = serializers.CharField(source='get_shipping_method_display', read_only=True)

    class Meta:
        model = Shipment
        fields = '__all__'
        read_only_fields = ['tracking_number', 'created_at', 'updated_at']


class CreateShipmentSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()
    order_number = serializers.CharField()
    customer_name = serializers.CharField()
    customer_phone = serializers.CharField()
    shipping_address = serializers.CharField()
    shipping_method = serializers.ChoiceField(choices=Shipment.METHOD_CHOICES, default='standard')
