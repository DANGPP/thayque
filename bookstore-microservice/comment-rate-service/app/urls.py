from django.urls import path
from .views import (
    ReviewListView, CreateReviewView, ReviewDetailView,
    BookRatingSummaryView, MarkHelpfulView, ReplyReviewView,
    HealthCheckView
)

urlpatterns = [
    path('reviews/', ReviewListView.as_view(), name='review-list'),
    path('reviews/create/', CreateReviewView.as_view(), name='review-create'),
    path('reviews/<int:pk>/', ReviewDetailView.as_view(), name='review-detail'),
    path('reviews/<int:pk>/helpful/', MarkHelpfulView.as_view(), name='review-helpful'),
    path('reviews/<int:pk>/reply/', ReplyReviewView.as_view(), name='review-reply'),
    path('books/<int:book_id>/rating/', BookRatingSummaryView.as_view(), name='book-rating'),
    path('health/', HealthCheckView.as_view(), name='health'),
]
