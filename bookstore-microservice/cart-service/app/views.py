from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.conf import settings
import requests
import logging

from .models import Cart, CartItem
from .serializers import (
    CartSerializer, CartItemSerializer, 
    AddToCartSerializer, UpdateCartItemSerializer
)

logger = logging.getLogger(__name__)


class CartCreateView(APIView):
    """Tạo giỏ hàng mới cho customer"""
    def post(self, request):
        customer_id = request.data.get('customer_id')
        if not customer_id:
            return Response({'error': 'customer_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        cart, created = Cart.objects.get_or_create(customer_id=customer_id)
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


class CartDetailView(APIView):
    """Xem giỏ hàng của customer"""
    def get(self, request, customer_id):
        try:
            cart = Cart.objects.get(customer_id=customer_id)
            serializer = CartSerializer(cart)
            return Response(serializer.data)
        except Cart.DoesNotExist:
            # Auto create cart if not exists
            cart = Cart.objects.create(customer_id=customer_id)
            serializer = CartSerializer(cart)
            return Response(serializer.data)


class AddToCartView(APIView):
    """Thêm sách vào giỏ hàng"""
    def post(self, request, customer_id):
        serializer = AddToCartSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        book_id = serializer.validated_data['book_id']
        quantity = serializer.validated_data['quantity']
        
        # Get or create cart
        cart, _ = Cart.objects.get_or_create(customer_id=customer_id)
        
        # Get book info from book-service
        try:
            book_url = getattr(settings, 'BOOK_SERVICE_URL', 'http://book-service:8000')
            response = requests.get(f"{book_url}/api/books/{book_id}/", timeout=5)
            if response.status_code != 200:
                return Response({'error': 'Không tìm thấy sách'}, status=status.HTTP_404_NOT_FOUND)
            book_data = response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to get book info: {e}")
            return Response({'error': 'Không thể kết nối đến book service'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        # Check stock
        if book_data.get('stock', 0) < quantity:
            return Response({'error': 'Không đủ hàng trong kho'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Add or update cart item
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            book_id=book_id,
            defaults={
                'book_title': book_data.get('title', ''),
                'book_price': book_data.get('discount_price') or book_data.get('price'),
                'book_image': book_data.get('cover_image'),
                'quantity': quantity
            }
        )
        
        if not created:
            cart_item.quantity += quantity
            cart_item.book_price = book_data.get('discount_price') or book_data.get('price')
            cart_item.save()
        
        return Response(CartSerializer(cart).data, status=status.HTTP_201_CREATED)


class UpdateCartItemView(APIView):
    """Cập nhật số lượng sản phẩm trong giỏ"""
    def put(self, request, customer_id, item_id):
        serializer = UpdateCartItemSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            cart = Cart.objects.get(customer_id=customer_id)
            cart_item = CartItem.objects.get(id=item_id, cart=cart)
            
            quantity = serializer.validated_data['quantity']
            if quantity == 0:
                cart_item.delete()
            else:
                cart_item.quantity = quantity
                cart_item.save()
            
            return Response(CartSerializer(cart).data)
        except (Cart.DoesNotExist, CartItem.DoesNotExist):
            return Response({'error': 'Không tìm thấy'}, status=status.HTTP_404_NOT_FOUND)


class RemoveCartItemView(APIView):
    """Xóa sản phẩm khỏi giỏ hàng"""
    def delete(self, request, customer_id, item_id):
        try:
            cart = Cart.objects.get(customer_id=customer_id)
            cart_item = CartItem.objects.get(id=item_id, cart=cart)
            cart_item.delete()
            return Response(CartSerializer(cart).data)
        except (Cart.DoesNotExist, CartItem.DoesNotExist):
            return Response({'error': 'Không tìm thấy'}, status=status.HTTP_404_NOT_FOUND)


class ClearCartView(APIView):
    """Xóa toàn bộ giỏ hàng"""
    def delete(self, request, customer_id):
        try:
            cart = Cart.objects.get(customer_id=customer_id)
            cart.items.all().delete()
            return Response(CartSerializer(cart).data)
        except Cart.DoesNotExist:
            return Response({'error': 'Không tìm thấy giỏ hàng'}, status=status.HTTP_404_NOT_FOUND)


class HealthCheckView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({'status': 'healthy', 'service': 'cart-service'})
