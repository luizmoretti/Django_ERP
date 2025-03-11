from django.urls import path
from . import views

app_name = 'vehicle'

urlpatterns = [
    # Vehicle URLs
    path('', views.VehicleListView.as_view(), name='vehicle-list'),
    path('<uuid:pk>/', views.VehicleDetailView.as_view(), name='vehicle-detail'),
    path('<uuid:pk>/assign-driver/', views.VehicleAssignDriverView.as_view(), name='vehicle-assign-driver'),
    
    # Maintenance record URLs
    path('<uuid:vehicle_id>/maintenance/', views.VehicleMaintenanceRecordListView.as_view(), name='maintenance-list'),
    path('maintenance/<uuid:pk>/', views.VehicleMaintenanceRecordDetailView.as_view(), name='maintenance-detail'),
    
    # Fuel record URLs
    path('<uuid:vehicle_id>/fuel/', views.VehicleFuelRecordListView.as_view(), name='fuel-list'),
    path('fuel/<uuid:pk>/', views.VehicleFuelRecordDetailView.as_view(), name='fuel-detail'),
]