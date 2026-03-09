from django.urls import path
from .views import (
    CartCreateView, CartDetailView, AddToCartView,
    UpdateCartItemView, RemoveCartItemView, ClearCartView,
    HealthCheckView
)

urlpatterns = [
    path('carts/', CartCreateView.as_view(), name='cart-create'),
    path('carts/<int:customer_id>/', CartDetailView.as_view(), name='cart-detail'),
    path('carts/<int:customer_id>/add/', AddToCartView.as_view(), name='cart-add'),
    path('carts/<int:customer_id>/items/<int:item_id>/', UpdateCartItemView.as_view(), name='cart-update-item'),
    path('carts/<int:customer_id>/items/<int:item_id>/remove/', RemoveCartItemView.as_view(), name='cart-remove-item'),
    path('carts/<int:customer_id>/clear/', ClearCartView.as_view(), name='cart-clear'),
    path('health/', HealthCheckView.as_view(), name='health'),
]
