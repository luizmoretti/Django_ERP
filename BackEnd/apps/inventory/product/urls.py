from django.urls import path
from . import views

urlpatterns = [
    # Product URLs
    path('', views.ProductListView.as_view(), name='product-list'),
    path('create/', views.ProductCreateView.as_view(), name='product-create'),
    path('retrieve/<uuid:pk>/', views.ProductRetrieveView.as_view(), name='product-detail'),
    path('update/<uuid:pk>/', views.ProductUpdateView.as_view(), name='product-update'),
    path('delete/<uuid:pk>/', views.ProductDestroyView.as_view(), name='product-delete'),
]