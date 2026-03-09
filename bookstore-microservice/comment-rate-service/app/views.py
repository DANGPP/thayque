from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.conf import settings
from django.db.models import Avg, Count
import requests
import logging

from .models import Review, ReviewReply, ReviewHelpful
from .serializers import (
    ReviewSerializer, CreateReviewSerializer, 
    ReviewReplySerializer, BookRatingSummarySerializer
)

logger = logging.getLogger(__name__)


class ReviewListView(APIView):
    """Danh sách đánh giá"""
    def get(self, request):
        book_id = request.query_params.get('book_id')
        customer_id = request.query_params.get('customer_id')
        
        reviews = Review.objects.filter(is_approved=True)
        
        if book_id:
            reviews = reviews.filter(book_id=book_id)
        if customer_id:
            reviews = reviews.filter(customer_id=customer_id)
        
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)


class CreateReviewView(APIView):
    """Tạo đánh giá mới"""
    def post(self, request):
        serializer = CreateReviewSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        # Check if already reviewed
        if Review.objects.filter(book_id=data['book_id'], customer_id=data['customer_id']).exists():
            return Response({'error': 'Bạn đã đánh giá sách này rồi'}, status=status.HTTP_400_BAD_REQUEST)
        
        review = Review.objects.create(
            book_id=data['book_id'],
            customer_id=data['customer_id'],
            customer_name=data['customer_name'],
            rating=data['rating'],
            title=data.get('title', ''),
            comment=data['comment']
        )
        
        # Update book rating
        self._update_book_rating(data['book_id'])
        
        return Response(ReviewSerializer(review).data, status=status.HTTP_201_CREATED)

    def _update_book_rating(self, book_id):
        """Cập nhật rating trung bình của sách"""
        stats = Review.objects.filter(book_id=book_id, is_approved=True).aggregate(
            avg_rating=Avg('rating'),
            total_reviews=Count('id')
        )
        
        try:
            book_url = getattr(settings, 'BOOK_SERVICE_URL', 'http://book-service:8000')
            requests.post(
                f"{book_url}/api/books/{book_id}/rating/",
                json={
                    'avg_rating': float(stats['avg_rating'] or 0),
                    'total_reviews': stats['total_reviews']
                },
                timeout=5
            )
        except requests.RequestException as e:
            logger.warning(f"Failed to update book rating: {e}")


class ReviewDetailView(APIView):
    """Chi tiết đánh giá"""
    def get(self, request, pk):
        try:
            review = Review.objects.get(pk=pk)
            serializer = ReviewSerializer(review)
            return Response(serializer.data)
        except Review.DoesNotExist:
            return Response({'error': 'Không tìm thấy'}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        try:
            review = Review.objects.get(pk=pk)
            
            # Only owner can update
            if review.customer_id != request.data.get('customer_id'):
                return Response({'error': 'Không có quyền'}, status=status.HTTP_403_FORBIDDEN)
            
            review.rating = request.data.get('rating', review.rating)
            review.title = request.data.get('title', review.title)
            review.comment = request.data.get('comment', review.comment)
            review.save()
            
            # Update book rating
            self._update_book_rating(review.book_id)
            
            return Response(ReviewSerializer(review).data)
        except Review.DoesNotExist:
            return Response({'error': 'Không tìm thấy'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        try:
            review = Review.objects.get(pk=pk)
            book_id = review.book_id
            review.delete()
            
            # Update book rating
            self._update_book_rating(book_id)
            
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Review.DoesNotExist:
            return Response({'error': 'Không tìm thấy'}, status=status.HTTP_404_NOT_FOUND)

    def _update_book_rating(self, book_id):
        stats = Review.objects.filter(book_id=book_id, is_approved=True).aggregate(
            avg_rating=Avg('rating'),
            total_reviews=Count('id')
        )
        
        try:
            book_url = getattr(settings, 'BOOK_SERVICE_URL', 'http://book-service:8000')
            requests.post(
                f"{book_url}/api/books/{book_id}/rating/",
                json={
                    'avg_rating': float(stats['avg_rating'] or 0),
                    'total_reviews': stats['total_reviews']
                },
                timeout=5
            )
        except requests.RequestException as e:
            logger.warning(f"Failed to update book rating: {e}")


class BookRatingSummaryView(APIView):
    """Tổng hợp rating của sách"""
    def get(self, request, book_id):
        reviews = Review.objects.filter(book_id=book_id, is_approved=True)
        
        stats = reviews.aggregate(
            avg_rating=Avg('rating'),
            total_reviews=Count('id')
        )
        
        # Rating distribution
        distribution = {str(i): 0 for i in range(1, 6)}
        for r in reviews.values('rating').annotate(count=Count('id')):
            distribution[str(r['rating'])] = r['count']
        
        return Response({
            'book_id': book_id,
            'avg_rating': round(stats['avg_rating'] or 0, 2),
            'total_reviews': stats['total_reviews'],
            'rating_distribution': distribution
        })


class MarkHelpfulView(APIView):
    """Đánh dấu review hữu ích"""
    def post(self, request, pk):
        customer_id = request.data.get('customer_id')
        
        try:
            review = Review.objects.get(pk=pk)
            
            helpful, created = ReviewHelpful.objects.get_or_create(
                review=review,
                customer_id=customer_id
            )
            
            if created:
                review.helpful_count += 1
                review.save()
                return Response({'message': 'Đã đánh dấu hữu ích'})
            else:
                helpful.delete()
                review.helpful_count = max(0, review.helpful_count - 1)
                review.save()
                return Response({'message': 'Đã bỏ đánh dấu hữu ích'})
        except Review.DoesNotExist:
            return Response({'error': 'Không tìm thấy'}, status=status.HTTP_404_NOT_FOUND)


class ReplyReviewView(APIView):
    """Phản hồi đánh giá (staff)"""
    def post(self, request, pk):
        try:
            review = Review.objects.get(pk=pk)
            
            reply = ReviewReply.objects.create(
                review=review,
                staff_id=request.data.get('staff_id'),
                staff_name=request.data.get('staff_name', 'Admin'),
                content=request.data.get('content')
            )
            
            return Response(ReviewReplySerializer(reply).data, status=status.HTTP_201_CREATED)
        except Review.DoesNotExist:
            return Response({'error': 'Không tìm thấy'}, status=status.HTTP_404_NOT_FOUND)


class HealthCheckView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({'status': 'healthy', 'service': 'comment-rate-service'})
