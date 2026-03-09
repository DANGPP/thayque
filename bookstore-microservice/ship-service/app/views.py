from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import requests
import logging

from .models import Shipment, ShipmentTracking
from .serializers import ShipmentSerializer, CreateShipmentSerializer

logger = logging.getLogger(__name__)


class ShipmentListView(APIView):
    """Danh sách vận chuyển"""
    def get(self, request):
        status_filter = request.query_params.get('status')
        
        shipments = Shipment.objects.all()
        
        if status_filter:
            shipments = shipments.filter(status=status_filter)
        
        serializer = ShipmentSerializer(shipments, many=True)
        return Response(serializer.data)


class CreateShipmentView(APIView):
    """Tạo vận chuyển mới"""
    def post(self, request):
        serializer = CreateShipmentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        # Calculate estimated delivery
        method = data.get('shipping_method', 'standard')
        if method == 'same_day':
            estimated = timezone.now().date()
        elif method == 'express':
            estimated = timezone.now().date() + timedelta(days=2)
        else:
            estimated = timezone.now().date() + timedelta(days=5)
        
        shipment = Shipment.objects.create(
            order_id=data['order_id'],
            order_number=data['order_number'],
            customer_name=data['customer_name'],
            customer_phone=data['customer_phone'],
            shipping_address=data['shipping_address'],
            shipping_method=method,
            estimated_delivery=estimated
        )
        
        ShipmentTracking.objects.create(
            shipment=shipment,
            status='pending',
            description='Đơn hàng đã được tạo, chờ xử lý'
        )
        
        return Response(ShipmentSerializer(shipment).data, status=status.HTTP_201_CREATED)


class ShipmentDetailView(APIView):
    """Chi tiết vận chuyển"""
    def get(self, request, pk):
        try:
            shipment = Shipment.objects.get(pk=pk)
            serializer = ShipmentSerializer(shipment)
            return Response(serializer.data)
        except Shipment.DoesNotExist:
            return Response({'error': 'Không tìm thấy'}, status=status.HTTP_404_NOT_FOUND)


class ShipmentByOrderView(APIView):
    """Tìm vận chuyển theo order"""
    def get(self, request, order_id):
        try:
            shipment = Shipment.objects.get(order_id=order_id)
            serializer = ShipmentSerializer(shipment)
            return Response(serializer.data)
        except Shipment.DoesNotExist:
            return Response({'error': 'Không tìm thấy'}, status=status.HTTP_404_NOT_FOUND)


class TrackShipmentView(APIView):
    """Theo dõi vận chuyển theo tracking number"""
    def get(self, request, tracking_number):
        try:
            shipment = Shipment.objects.get(tracking_number=tracking_number)
            serializer = ShipmentSerializer(shipment)
            return Response(serializer.data)
        except Shipment.DoesNotExist:
            return Response({'error': 'Không tìm thấy mã vận đơn'}, status=status.HTTP_404_NOT_FOUND)


class UpdateShipmentStatusView(APIView):
    """Cập nhật trạng thái vận chuyển"""
    def put(self, request, pk):
        try:
            shipment = Shipment.objects.get(pk=pk)
            new_status = request.data.get('status')
            location = request.data.get('location', '')
            description = request.data.get('description', '')
            
            if new_status not in dict(Shipment.STATUS_CHOICES):
                return Response({'error': 'Trạng thái không hợp lệ'}, status=status.HTTP_400_BAD_REQUEST)
            
            shipment.status = new_status
            
            if new_status == 'delivered':
                shipment.delivered_at = timezone.now()
            
            shipment.save()
            
            ShipmentTracking.objects.create(
                shipment=shipment,
                status=new_status,
                location=location,
                description=description or f"Trạng thái: {dict(Shipment.STATUS_CHOICES)[new_status]}"
            )
            
            # Update order status
            if new_status in ['in_transit', 'out_for_delivery', 'delivered']:
                try:
                    order_url = getattr(settings, 'ORDER_SERVICE_URL', 'http://order-service:8000')
                    order_status = 'shipped' if new_status != 'delivered' else 'delivered'
                    requests.put(
                        f"{order_url}/api/orders/{shipment.order_id}/status/",
                        json={'status': order_status},
                        timeout=5
                    )
                except requests.RequestException as e:
                    logger.warning(f"Failed to update order: {e}")
            
            return Response(ShipmentSerializer(shipment).data)
        except Shipment.DoesNotExist:
            return Response({'error': 'Không tìm thấy'}, status=status.HTTP_404_NOT_FOUND)


class HealthCheckView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({'status': 'healthy', 'service': 'ship-service'})
