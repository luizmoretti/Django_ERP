from django.urls import path
from . import views

app_name = 'product'

urlpatterns = [
    # Product URLs
    path('', views.ProductListView.as_view(), name='list_products'),
    path('create/', views.ProductCreateView.as_view(), name='create_product'),
    path('retrieve/<uuid:pk>/', views.ProductRetrieveView.as_view(), name='retrieve_product'),
    path('update/<uuid:pk>/', views.ProductUpdateView.as_view(), name='update_product'),
    path('delete/<uuid:pk>/', views.ProductDestroyView.as_view(), name='delete_product'),
    
    # Home Depot Actions
    path('home-depot/', views.HomeDepotActionsView.as_view(), name='hd_actions'),
]