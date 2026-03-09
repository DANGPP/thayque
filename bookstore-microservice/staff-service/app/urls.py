from django.urls import path
from .views import (
    StaffLoginView, StaffListView, StaffDetailView,
    StaffActivityView, HealthCheckView
)

urlpatterns = [
    path('staff/', StaffListView.as_view(), name='staff-list'),
    path('staff/<int:pk>/', StaffDetailView.as_view(), name='staff-detail'),
    path('staff/<int:staff_id>/activities/', StaffActivityView.as_view(), name='staff-activities'),
    path('login/', StaffLoginView.as_view(), name='staff-login'),
    path('health/', HealthCheckView.as_view(), name='health'),
]
