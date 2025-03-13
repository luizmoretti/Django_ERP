from django.urls import path
from . import views

app_name = 'outflows'

urlpatterns = [
    path('', views.OutflowListView.as_view(), name='list_outflows'),
    path('create/', views.OutflowCreateView.as_view(), name='create_outflow'),
    path('retrieve/<uuid:pk>/', views.OutflowRetrieveView.as_view(), name='retrieve_outflow'),
    path('update/<uuid:pk>/', views.OutflowUpdateView.as_view(), name='update_outflow'),
    path('delete/<uuid:pk>/', views.OutflowDestroyView.as_view(), name='delete_outflow'),

    
    # Actions Endpoints
    path('approve/<uuid:pk>/', views.OutflowApproveView.as_view(), name='approve_outflow'),
    path('reject/<uuid:pk>/', views.OutflowRejectView.as_view(), name='reject_outflow'),
]