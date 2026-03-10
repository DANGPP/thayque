from django.urls import path
from .views import (
    CustomerRegistrationView,
    CustomerLoginView,
    CustomerListView,
    CustomerDetailView,
    CustomerProfileView,
    UpdateCustomerView,
    HealthCheckView
)

urlpatterns = [
    path('customers/', CustomerListView.as_view(), name='customer-list'),
    path('customers/<int:pk>/', CustomerDetailView.as_view(), name='customer-detail'),
    path('customers/<int:pk>/update/', UpdateCustomerView.as_view(), name='customer-update'),
    path('customers/<int:customer_id>/profile/', CustomerProfileView.as_view(), name='customer-profile'),
    path('register/', CustomerRegistrationView.as_view(), name='register'),
    path('login/', CustomerLoginView.as_view(), name='login'),
    path('health/', HealthCheckView.as_view(), name='health'),
]
