from django.urls import path
from . import views

app_name = 'delivery'

urlpatterns = [
    # Basic CRUD routes
    path('', views.DeliveryListView.as_view(), name='list_deliveries'),
    path('create/', views.DeliveryCreateView.as_view(), name='create_delivery'),
    path('retrieve/<uuid:pk>/', views.DeliveryRetrieveView.as_view(), name='retrieve_delivery'),
    path('update/<uuid:pk>/', views.DeliveryUpdateView.as_view(), name='update_delivery'),
    path('delete/<uuid:pk>/', views.DeliveryDestroyView.as_view(), name='delete_delivery'),
    
    # Real-time tracking routes
    path('location/<uuid:pk>/', views.DeliveryLocationUpdateView.as_view(), name='update_location'),
    path('status/<uuid:pk>/', views.DeliveryStatusUpdateView.as_view(), name='update_status'),
    
    # Checkpoint route
    path('checkpoints/<uuid:pk>/', views.DeliveryCheckpointsListView.as_view(), name='list_checkpoints'),
    
    # Report route
    path('report/<uuid:pk>/', views.DeliveryReportView.as_view(), name='generate_report'),
]
