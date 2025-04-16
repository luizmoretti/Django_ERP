from django.urls import path
from . import views

app_name = 'vehicle'

urlpatterns = [
    # Vehicle URLs
    path('', views.VehicleListView.as_view(), name='vehicle-list'),
    path('create/', views.VehicleCreateView.as_view(), name='vehicle-create'),
    path('retrieve/<uuid:pk>/', views.VehicleRetrieveView.as_view(), name='vehicle-detail'),
    path('update/<uuid:pk>/', views.VehicleUpdateView.as_view(), name='vehicle-update'),
    path('delete/<uuid:pk>/', views.VehicleDestroyView.as_view(), name='vehicle-delete'),
]