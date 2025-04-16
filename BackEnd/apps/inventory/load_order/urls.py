from django.urls import path
from . import views

app_name = 'load_order'

urlpatterns = [
    path('', views.LoadOrderListView.as_view(), name='list_load_orders'),
    path('create/', views.LoadOrderCreateView.as_view(), name='create_load_order'),
    path('retrieve/<uuid:pk>/', views.LoadOrderRetrieveView.as_view(), name='retrieve_load_order'),
    path('update/<uuid:pk>/', views.LoadOrderUpdateView.as_view(), name='update_load_order'),
    path('delete/<uuid:pk>/', views.LoadOrderDestroyView.as_view(), name='delete_load_order'),
]