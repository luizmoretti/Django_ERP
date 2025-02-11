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
    
    # Purchase Order Actions
    path('<uuid:pk>/approve/', views.PurchaseOrderApproveView.as_view(), name='approve'),
    path('<uuid:pk>/reject/', views.PurchaseOrderRejectView.as_view(), name='reject'),
    path('<uuid:pk>/cancel/', views.PurchaseOrderCancelView.as_view(), name='cancel'),
    
    # Purchase Order Items
    path('<uuid:pk>/items/add/', views.PurchaseOrderAddItemView.as_view(), name='add_item'),
    path('items/<uuid:pk>/update/', views.PurchaseOrderUpdateItemView.as_view(), name='update_item'),
    path('items/<uuid:pk>/remove/', views.PurchaseOrderRemoveItemView.as_view(), name='remove_item'),
]
