from django.urls import path
from . import views

app_name = 'warehouse'

urlpatterns = [
    path('', views.WarehouseListView.as_view(), name='warehouse_list'),
    path('create/', views.WarehouseCreateView.as_view(), name='warehouse_create'),
    path('retrieve/<uuid:pk>/', views.WarehouseRetrieveView.as_view(), name='warehouse_retrieve'),
    path('update/<uuid:pk>/', views.WarehouseUpdateView.as_view(), name='warehouse_update'),
    path('delete/<uuid:pk>/', views.WarehouseDeleteView.as_view(), name='warehouse_delete'),
]