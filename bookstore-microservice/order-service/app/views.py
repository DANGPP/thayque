from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.conf import settings
from django.db import transaction
import requests
import logging

from .models import Order, OrderItem, OrderStatusHistory
from .serializers import (
    OrderSerializer, OrderListSerializer, 
    CreateOrderSerializer, OrderItemSerializer
)

logger = logging.getLogger(__name__)


class OrderListView(APIView):
    """Danh sách đơn hàng"""
    def get(self, request):
        customer_id = request.query_params.get('customer_id')
        status_filter = request.query_params.get('status')
        
        orders = Order.objects.all()
        
        if customer_id:
            orders = orders.filter(customer_id=customer_id)
        if status_filter:
            orders = orders.filter(status=status_filter)
        
        serializer = OrderListSerializer(orders, many=True)
        return Response(serializer.data)


class CreateOrderView(APIView):
    """Tạo đơn hàng mới từ giỏ hàng"""
    @transaction.atomic
    def post(self, request):
        serializer = CreateOrderSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        customer_id = data['customer_id']
        
        # 1. Get cart from cart-service
        try:
            cart_url = getattr(settings, 'CART_SERVICE_URL', 'http://cart-service:8000')
            cart_response = requests.get(f"{cart_url}/api/carts/{customer_id}/", timeout=5)
            if cart_response.status_code != 200:
                return Response({'error': 'Không tìm thấy giỏ hàng'}, status=status.HTTP_404_NOT_FOUND)
            cart_data = cart_response.json()
        except requests.RequestException as e:
            logger.error(f"Cart service error: {e}")
            return Response({'error': 'Không thể kết nối cart service'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        cart_items = cart_data.get('items', [])
        if not cart_items:
            return Response({'error': 'Giỏ hàng trống'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Calculate totals
        subtotal = sum(float(item['book_price']) * item['quantity'] for item in cart_items)
        shipping_fee = 30000 if data.get('shipping_method') == 'express' else 15000
        total = subtotal + shipping_fee
        
        # 2. Create order
        order = Order.objects.create(
            customer_id=customer_id,
            customer_name=data['customer_name'],
            customer_email=data['customer_email'],
            customer_phone=data['customer_phone'],
            shipping_address=data['shipping_address'],
            shipping_method=data.get('shipping_method', 'standard'),
            shipping_fee=shipping_fee,
            payment_method=data.get('payment_method', 'cod'),
            subtotal=subtotal,
            total=total,
            notes=data.get('notes', '')
        )
        
        # 3. Create order items
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                book_id=item['book_id'],
                book_title=item['book_title'],
                book_price=item['book_price'],
                book_image=item.get('book_image'),
                quantity=item['quantity']
            )
        
        # 4. Create status history
        OrderStatusHistory.objects.create(
            order=order,
            status='pending',
            note='Đơn hàng được tạo'
        )
        
        # 5. Create payment record
        try:
            pay_url = getattr(settings, 'PAY_SERVICE_URL', 'http://pay-service:8000')
            pay_response = requests.post(
                f"{pay_url}/api/payments/",
                json={
                    'order_id': order.id,
                    'order_number': order.order_number,
                    'amount': float(total),
                    'payment_method': data.get('payment_method', 'cod'),
                    'customer_id': customer_id
                },
                timeout=5
            )
            if pay_response.status_code == 201:
                payment_data = pay_response.json()
                order.payment_id = payment_data.get('id')
                order.save()
        except requests.RequestException as e:
            logger.warning(f"Payment service error: {e}")
        
        # 6. Create shipping record
        try:
            ship_url = getattr(settings, 'SHIP_SERVICE_URL', 'http://ship-service:8000')
            ship_response = requests.post(
                f"{ship_url}/api/shipments/",
                json={
                    'order_id': order.id,
                    'order_number': order.order_number,
                    'shipping_address': data['shipping_address'],
                    'shipping_method': data.get('shipping_method', 'standard'),
                    'customer_name': data['customer_name'],
                    'customer_phone': data['customer_phone']
                },
                timeout=5
            )
            if ship_response.status_code == 201:
                ship_data = ship_response.json()
                order.shipping_id = ship_data.get('id')
                order.save()
        except requests.RequestException as e:
            logger.warning(f"Shipping service error: {e}")
        
        # 7. Update book stock
        try:
            book_url = getattr(settings, 'BOOK_SERVICE_URL', 'http://book-service:8000')
            for item in cart_items:
                requests.post(
                    f"{book_url}/api/books/{item['book_id']}/stock/",
                    json={'quantity': item['quantity'], 'action': 'decrease'},
                    timeout=5
                )
        except requests.RequestException as e:
            logger.warning(f"Book service error: {e}")
        
        # 8. Clear cart
        try:
            requests.delete(f"{cart_url}/api/carts/{customer_id}/clear/", timeout=5)
        except requests.RequestException as e:
            logger.warning(f"Failed to clear cart: {e}")
        
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


class OrderDetailView(APIView):
    """Chi tiết đơn hàng"""
    def get(self, request, pk):
        try:
            order = Order.objects.get(pk=pk)
            serializer = OrderSerializer(order)
            return Response(serializer.data)
        except Order.DoesNotExist:
            return Response({'error': 'Không tìm thấy đơn hàng'}, status=status.HTTP_404_NOT_FOUND)


class OrderByNumberView(APIView):
    """Tìm đơn hàng theo mã"""
    def get(self, request, order_number):
        try:
            order = Order.objects.get(order_number=order_number)
            serializer = OrderSerializer(order)
            return Response(serializer.data)
        except Order.DoesNotExist:
            return Response({'error': 'Không tìm thấy đơn hàng'}, status=status.HTTP_404_NOT_FOUND)


class UpdateOrderStatusView(APIView):
    """Cập nhật trạng thái đơn hàng"""
    def put(self, request, pk):
        try:
            order = Order.objects.get(pk=pk)
            new_status = request.data.get('status')
            note = request.data.get('note', '')
            
            if new_status not in dict(Order.STATUS_CHOICES):
                return Response({'error': 'Trạng thái không hợp lệ'}, status=status.HTTP_400_BAD_REQUEST)
            
            order.status = new_status
            order.save()
            
            OrderStatusHistory.objects.create(
                order=order,
                status=new_status,
                note=note,
                created_by=request.data.get('created_by', 'system')
            )
            
            return Response(OrderSerializer(order).data)
        except Order.DoesNotExist:
            return Response({'error': 'Không tìm thấy đơn hàng'}, status=status.HTTP_404_NOT_FOUND)


class CancelOrderView(APIView):
    """Hủy đơn hàng"""
    def post(self, request, pk):
        try:
            order = Order.objects.get(pk=pk)
            
            if order.status in ['shipped', 'delivered']:
                return Response({'error': 'Không thể hủy đơn hàng đã giao'}, status=status.HTTP_400_BAD_REQUEST)
            
            order.status = 'cancelled'
            order.save()
            
            OrderStatusHistory.objects.create(
                order=order,
                status='cancelled',
                note=request.data.get('reason', 'Khách hủy đơn')
            )
            
            # Restore book stock
            try:
                book_url = getattr(settings, 'BOOK_SERVICE_URL', 'http://book-service:8000')
                for item in order.items.all():
                    requests.post(
                        f"{book_url}/api/books/{item.book_id}/stock/",
                        json={'quantity': item.quantity, 'action': 'increase'},
                        timeout=5
                    )
            except requests.RequestException as e:
                logger.warning(f"Failed to restore stock: {e}")
            
            return Response(OrderSerializer(order).data)
        except Order.DoesNotExist:
            return Response({'error': 'Không tìm thấy đơn hàng'}, status=status.HTTP_404_NOT_FOUND)


class HealthCheckView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({'status': 'healthy', 'service': 'order-service'})
