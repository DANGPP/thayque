from django.urls import path
from .views import (
    # Customer views
    HomeView, BookListView, BookDetailView,
    CustomerRegisterView, CustomerLoginView, CustomerLogoutView,
    CartView, AddToCartView, UpdateCartView, RemoveCartItemView,
    CheckoutView, OrderHistoryView, OrderDetailView, WriteReviewView,
    # Admin views
    AdminLoginView, AdminLogoutView, AdminDashboardView,
    AdminBooksView, AdminBookCreateView, AdminOrdersView, AdminOrderDetailView,
    AdminCustomersView, AdminCategoriesView, AdminReviewsView,
    # API
    APIProxyView,
)

urlpatterns = [
    # Customer routes
    path('', HomeView.as_view(), name='home'),
    path('books/', BookListView.as_view(), name='books'),
    path('books/<int:pk>/', BookDetailView.as_view(), name='book_detail'),
    path('register/', CustomerRegisterView.as_view(), name='customer_register'),
    path('login/', CustomerLoginView.as_view(), name='customer_login'),
    path('logout/', CustomerLogoutView.as_view(), name='customer_logout'),
    path('cart/', CartView.as_view(), name='cart'),
    path('cart/add/', AddToCartView.as_view(), name='add_to_cart'),
    path('cart/update/<int:item_id>/', UpdateCartView.as_view(), name='update_cart'),
    path('cart/remove/<int:item_id>/', RemoveCartItemView.as_view(), name='remove_cart_item'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('orders/', OrderHistoryView.as_view(), name='order_history'),
    path('orders/<str:order_number>/', OrderDetailView.as_view(), name='order_detail'),
    path('books/<int:book_id>/review/', WriteReviewView.as_view(), name='write_review'),
    
    # Admin routes
    path('admin-panel/login/', AdminLoginView.as_view(), name='admin_login'),
    path('admin-panel/logout/', AdminLogoutView.as_view(), name='admin_logout'),
    path('admin-panel/', AdminDashboardView.as_view(), name='admin_dashboard'),
    path('admin-panel/books/', AdminBooksView.as_view(), name='admin_books'),
    path('admin-panel/books/create/', AdminBookCreateView.as_view(), name='admin_book_create'),
    path('admin-panel/orders/', AdminOrdersView.as_view(), name='admin_orders'),
    path('admin-panel/orders/<int:pk>/', AdminOrderDetailView.as_view(), name='admin_order_detail'),
    path('admin-panel/customers/', AdminCustomersView.as_view(), name='admin_customers'),
    path('admin-panel/categories/', AdminCategoriesView.as_view(), name='admin_categories'),
    path('admin-panel/reviews/', AdminReviewsView.as_view(), name='admin_reviews'),
    
    # API proxy
    path('api/<str:service>/<path:path>', APIProxyView.as_view(), name='api_proxy'),
]
