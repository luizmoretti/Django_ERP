from django.urls import path
from . import views

urlpatterns = [
    path('', views.InflowListView.as_view(), name='list_inflows'),
    path('create/', views.InflowCreateView.as_view(), name='create_inflow'),
    path('retrieve/<uuid:pk>/', views.InflowRetrieveView.as_view(), name='retrieve_inflow'),
    path('update/<uuid:pk>/', views.InflowUpdateView.as_view(), name='update_inflow'),
    path('delete/<uuid:pk>/', views.InflowDestroyView.as_view(), name='delete_inflow'),
]