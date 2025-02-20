from django.urls import path

from . import views

app_name = 'transfer'

urlpatterns = [
    path('', views.TransferListView.as_view(), name='list_transfers'),
    path('create/', views.TransferCreateView.as_view(), name='create_transfer'),
    path('retrieve/<uuid:pk>/', views.TransferRetrieveView.as_view(), name='retrieve_transfer'),
    path('update/<uuid:pk>/', views.TransferUpdateView.as_view(), name='update_transfer'),
    path('delete/<uuid:pk>/', views.TransferDestroyView.as_view(), name='delete_transfer'),
]