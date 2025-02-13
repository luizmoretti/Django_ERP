from django.urls import path
from . import views

app_name = 'supplier'

urlpatterns = [
    # Supplier URLs
    path('', views.SupplierListView.as_view(), name='supplier-list'),
    path('create/', views.SupplierCreateView.as_view(), name='supplier-create'),
    path('retrieve/<uuid:pk>/', views.SupplierRetrieveView.as_view(), name='supplier-detail'),
    path('update/<uuid:pk>/', views.SupplierUpdateView.as_view(), name='supplier-update'),
    path('delete/<uuid:pk>/', views.SupplierDestroyView.as_view(), name='supplier-delete'),
]