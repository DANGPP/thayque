from django.urls import path
from .views import (
    PaymentListView, CreatePaymentView, PaymentDetailView,
    PaymentByOrderView, ProcessPaymentView, ConfirmCODView,
    CreateRefundView, HealthCheckView
)

urlpatterns = [
    path('payments/', PaymentListView.as_view(), name='payment-list'),
    path('payments/create/', CreatePaymentView.as_view(), name='payment-create'),
    path('payments/<int:pk>/', PaymentDetailView.as_view(), name='payment-detail'),
    path('payments/<int:pk>/process/', ProcessPaymentView.as_view(), name='payment-process'),
    path('payments/<int:pk>/confirm-cod/', ConfirmCODView.as_view(), name='payment-confirm-cod'),
    path('payments/order/<int:order_id>/', PaymentByOrderView.as_view(), name='payment-by-order'),
    path('refunds/', CreateRefundView.as_view(), name='refund-create'),
    path('health/', HealthCheckView.as_view(), name='health'),
]
