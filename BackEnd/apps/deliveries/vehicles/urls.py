from django.urls import path
from . import views

urlpatterns = [
    path('', views.VehicleListView.as_view(), name='list_vehicles'),
    path('create/', views.VehicleCreateView.as_view(), name='create_vehicle'),
    path('retrieve/<uuid:pk>/', views.VehicleRetrieveView.as_view(), name='retrieve_vehicle'),
    path('update/<uuid:pk>/', views.VehicleUpdateView.as_view(), name='update_vehicle'),
    path('delete/<uuid:pk>/', views.VehicleDeleteView.as_view(), name='delete_vehicle'),
]