from django.urls import path
from .views import (
    CategoryListCreateView, CategoryDetailView,
    AuthorListCreateView, AuthorDetailView,
    PublisherListCreateView,
    BookListCreateView, BookDetailView,
    BookStockUpdateView, BookRatingUpdateView,
    HealthCheckView
)

urlpatterns = [
    path('categories/', CategoryListCreateView.as_view(), name='category-list'),
    path('categories/<int:pk>/', CategoryDetailView.as_view(), name='category-detail'),
    path('authors/', AuthorListCreateView.as_view(), name='author-list'),
    path('authors/<int:pk>/', AuthorDetailView.as_view(), name='author-detail'),
    path('publishers/', PublisherListCreateView.as_view(), name='publisher-list'),
    path('books/', BookListCreateView.as_view(), name='book-list'),
    path('books/<int:pk>/', BookDetailView.as_view(), name='book-detail'),
    path('books/<int:pk>/stock/', BookStockUpdateView.as_view(), name='book-stock'),
    path('books/<int:pk>/rating/', BookRatingUpdateView.as_view(), name='book-rating'),
    path('health/', HealthCheckView.as_view(), name='health'),
]
