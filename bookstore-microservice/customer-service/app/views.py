from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate
from django.conf import settings
import requests
import logging

from .models import Customer, CustomerProfile
from .serializers import (
    CustomerSerializer, 
    CustomerRegistrationSerializer,
    CustomerLoginSerializer,
    CustomerProfileSerializer
)

logger = logging.getLogger(__name__)


class CustomerRegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = CustomerRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            customer = serializer.save()
            
            # Call cart-service to create cart for customer
            try:
                cart_url = getattr(settings, 'CART_SERVICE_URL', 'http://cart-service:8000')
                response = requests.post(
                    f"{cart_url}/api/carts/",
                    json={"customer_id": customer.id},
                    timeout=5
                )
                if response.status_code == 201:
                    logger.info(f"Cart created for customer {customer.id}")
            except requests.RequestException as e:
                logger.warning(f"Failed to create cart for customer {customer.id}: {e}")

            return Response({
                'message': 'Đăng ký thành công',
                'customer': CustomerSerializer(customer).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomerLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = CustomerLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(
                username=serializer.validated_data['username'],
                password=serializer.validated_data['password']
            )
            if user and isinstance(user, Customer):
                return Response({
                    'message': 'Đăng nhập thành công',
                    'customer': CustomerSerializer(user).data
                })
            return Response(
                {'error': 'Tên đăng nhập hoặc mật khẩu không đúng'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomerListView(APIView):
    def get(self, request):
        customers = Customer.objects.all()
        serializer = CustomerSerializer(customers, many=True)
        return Response(serializer.data)


class CustomerDetailView(APIView):
    def get(self, request, pk):
        try:
            customer = Customer.objects.get(pk=pk)
            serializer = CustomerSerializer(customer)
            return Response(serializer.data)
        except Customer.DoesNotExist:
            return Response(
                {'error': 'Không tìm thấy khách hàng'},
                status=status.HTTP_404_NOT_FOUND
            )

    def put(self, request, pk):
        try:
            customer = Customer.objects.get(pk=pk)
            serializer = CustomerSerializer(customer, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Customer.DoesNotExist:
            return Response(
                {'error': 'Không tìm thấy khách hàng'},
                status=status.HTTP_404_NOT_FOUND
            )

    def delete(self, request, pk):
        try:
            customer = Customer.objects.get(pk=pk)
            customer.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Customer.DoesNotExist:
            return Response(
                {'error': 'Không tìm thấy khách hàng'},
                status=status.HTTP_404_NOT_FOUND
            )


class CustomerProfileView(APIView):
    def get(self, request, customer_id):
        try:
            profile = CustomerProfile.objects.get(customer_id=customer_id)
            serializer = CustomerProfileSerializer(profile)
            return Response(serializer.data)
        except CustomerProfile.DoesNotExist:
            return Response(
                {'error': 'Không tìm thấy profile'},
                status=status.HTTP_404_NOT_FOUND
            )

    def put(self, request, customer_id):
        try:
            profile = CustomerProfile.objects.get(customer_id=customer_id)
            serializer = CustomerProfileSerializer(profile, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except CustomerProfile.DoesNotExist:
            return Response(
                {'error': 'Không tìm thấy profile'},
                status=status.HTTP_404_NOT_FOUND
            )


class HealthCheckView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({'status': 'healthy', 'service': 'customer-service'})
