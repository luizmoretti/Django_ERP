from django.urls import path
from . import views

urlpatterns = [
    path('', views.OutflowListView.as_view(), name='list_outflows'),
    path('create/', views.OutflowCreateView.as_view(), name='create_outflow'),
    path('retrieve/<uuid:pk>/', views.OutflowRetrieveView.as_view(), name='retrieve_outflow'),
    path('update/<uuid:pk>/', views.OutflowUpdateView.as_view(), name='update_outflow'),
    path('delete/<uuid:pk>/', views.OutflowDestroyView.as_view(), name='delete_outflow'),
]