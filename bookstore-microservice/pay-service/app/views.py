from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.conf import settings
from django.utils import timezone
import requests
import logging

from .models import Payment, PaymentHistory, Refund
from .serializers import (
    PaymentSerializer, CreatePaymentSerializer,
    RefundSerializer, CreateRefundSerializer
)

logger = logging.getLogger(__name__)


class PaymentListView(APIView):
    """Danh sách thanh toán"""
    def get(self, request):
        customer_id = request.query_params.get('customer_id')
        status_filter = request.query_params.get('status')
        
        payments = Payment.objects.all()
        
        if customer_id:
            payments = payments.filter(customer_id=customer_id)
        if status_filter:
            payments = payments.filter(status=status_filter)
        
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data)


class CreatePaymentView(APIView):
    """Tạo thanh toán mới"""
    def post(self, request):
        serializer = CreatePaymentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        payment = Payment.objects.create(
            order_id=data['order_id'],
            order_number=data['order_number'],
            customer_id=data['customer_id'],
            amount=data['amount'],
            payment_method=data['payment_method']
        )
        
        PaymentHistory.objects.create(
            payment=payment,
            status='pending',
            note='Thanh toán được tạo'
        )
        
        return Response(PaymentSerializer(payment).data, status=status.HTTP_201_CREATED)


class PaymentDetailView(APIView):
    """Chi tiết thanh toán"""
    def get(self, request, pk):
        try:
            payment = Payment.objects.get(pk=pk)
            serializer = PaymentSerializer(payment)
            return Response(serializer.data)
        except Payment.DoesNotExist:
            return Response({'error': 'Không tìm thấy thanh toán'}, status=status.HTTP_404_NOT_FOUND)


class PaymentByOrderView(APIView):
    """Tìm thanh toán theo order"""
    def get(self, request, order_id):
        try:
            payment = Payment.objects.get(order_id=order_id)
            serializer = PaymentSerializer(payment)
            return Response(serializer.data)
        except Payment.DoesNotExist:
            return Response({'error': 'Không tìm thấy thanh toán'}, status=status.HTTP_404_NOT_FOUND)


class ProcessPaymentView(APIView):
    """Xử lý thanh toán (simulate payment gateway)"""
    def post(self, request, pk):
        try:
            payment = Payment.objects.get(pk=pk)
            
            if payment.status != 'pending':
                return Response({'error': 'Thanh toán đã được xử lý'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Simulate payment processing
            payment.status = 'processing'
            payment.save()
            
            PaymentHistory.objects.create(
                payment=payment,
                status='processing',
                note='Đang xử lý thanh toán'
            )
            
            # Simulate successful payment (in production, this would be callback from gateway)
            payment.status = 'completed'
            payment.paid_at = timezone.now()
            payment.save()
            
            PaymentHistory.objects.create(
                payment=payment,
                status='completed',
                note='Thanh toán thành công'
            )
            
            # Update order payment status
            try:
                order_url = getattr(settings, 'ORDER_SERVICE_URL', 'http://order-service:8000')
                requests.put(
                    f"{order_url}/api/orders/{payment.order_id}/",
                    json={'payment_status': 'completed'},
                    timeout=5
                )
            except requests.RequestException as e:
                logger.warning(f"Failed to update order: {e}")
            
            return Response(PaymentSerializer(payment).data)
        except Payment.DoesNotExist:
            return Response({'error': 'Không tìm thấy thanh toán'}, status=status.HTTP_404_NOT_FOUND)


class ConfirmCODView(APIView):
    """Xác nhận COD khi giao hàng thành công"""
    def post(self, request, pk):
        try:
            payment = Payment.objects.get(pk=pk)
            
            if payment.payment_method != 'cod':
                return Response({'error': 'Không phải thanh toán COD'}, status=status.HTTP_400_BAD_REQUEST)
            
            payment.status = 'completed'
            payment.paid_at = timezone.now()
            payment.save()
            
            PaymentHistory.objects.create(
                payment=payment,
                status='completed',
                note='COD - Đã nhận tiền khi giao hàng'
            )
            
            return Response(PaymentSerializer(payment).data)
        except Payment.DoesNotExist:
            return Response({'error': 'Không tìm thấy thanh toán'}, status=status.HTTP_404_NOT_FOUND)


class CreateRefundView(APIView):
    """Tạo yêu cầu hoàn tiền"""
    def post(self, request):
        serializer = CreateRefundSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            payment = Payment.objects.get(pk=serializer.validated_data['payment_id'])
            
            if payment.status != 'completed':
                return Response({'error': 'Chỉ có thể hoàn tiền cho thanh toán đã hoàn tất'}, status=status.HTTP_400_BAD_REQUEST)
            
            refund = Refund.objects.create(
                payment=payment,
                amount=serializer.validated_data['amount'],
                reason=serializer.validated_data['reason']
            )
            
            return Response(RefundSerializer(refund).data, status=status.HTTP_201_CREATED)
        except Payment.DoesNotExist:
            return Response({'error': 'Không tìm thấy thanh toán'}, status=status.HTTP_404_NOT_FOUND)


class HealthCheckView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({'status': 'healthy', 'service': 'pay-service'})
