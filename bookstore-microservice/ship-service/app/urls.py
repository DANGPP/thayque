from django.urls import path
from .views import (
    ShipmentListView, CreateShipmentView, ShipmentDetailView,
    ShipmentByOrderView, TrackShipmentView, UpdateShipmentStatusView,
    HealthCheckView
)

urlpatterns = [
    path('shipments/', ShipmentListView.as_view(), name='shipment-list'),
    path('shipments/create/', CreateShipmentView.as_view(), name='shipment-create'),
    path('shipments/<int:pk>/', ShipmentDetailView.as_view(), name='shipment-detail'),
    path('shipments/<int:pk>/status/', UpdateShipmentStatusView.as_view(), name='shipment-status'),
    path('shipments/order/<int:order_id>/', ShipmentByOrderView.as_view(), name='shipment-by-order'),
    path('shipments/track/<str:tracking_number>/', TrackShipmentView.as_view(), name='shipment-track'),
    path('health/', HealthCheckView.as_view(), name='health'),
]
