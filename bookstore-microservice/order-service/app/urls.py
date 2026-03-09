from django.urls import path
from .views import (
    OrderListView, CreateOrderView, OrderDetailView,
    OrderByNumberView, UpdateOrderStatusView, CancelOrderView,
    HealthCheckView
)

urlpatterns = [
    path('orders/', OrderListView.as_view(), name='order-list'),
    path('orders/create/', CreateOrderView.as_view(), name='order-create'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
    path('orders/<int:pk>/status/', UpdateOrderStatusView.as_view(), name='order-status'),
    path('orders/<int:pk>/cancel/', CancelOrderView.as_view(), name='order-cancel'),
    path('orders/number/<str:order_number>/', OrderByNumberView.as_view(), name='order-by-number'),
    path('health/', HealthCheckView.as_view(), name='health'),
]
