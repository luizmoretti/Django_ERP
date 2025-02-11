from django.urls import path
from . import views

app_name = 'purchase_order'

urlpatterns = [
    # Purchase Order URLs
    path('', views.PurchaseOrderListView.as_view(), name='list'),
    path('create/', views.PurchaseOrderCreateView.as_view(), name='create'),
    path('retrieve/<uuid:pk>/', views.PurchaseOrderRetrieveView.as_view(), name='detail'),
    path('update/<uuid:pk>/', views.PurchaseOrderUpdateView.as_view(), name='update'),
    path('delete/<uuid:pk>/', views.PurchaseOrderDeleteView.as_view(), name='delete'),
]
