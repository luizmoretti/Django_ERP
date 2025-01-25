from django.urls import path
from . import views

app_name = 'hr'

urlpatterns = [
    # HR URLs
    path('', views.HRListView.as_view(), name='hr-list'),
    path('create/', views.HRCreateView.as_view(), name='hr-create'),
    path('retrieve/<uuid:pk>/', views.HRRetrieveView.as_view(), name='hr-retrieve'),
    path('update/<uuid:pk>/', views.HRUpdateView.as_view(), name='hr-update'),
    path('delete/<uuid:pk>/', views.HRDestroyView.as_view(), name='hr-delete'),
    path('process-payment/<uuid:pk>/', views.HRProcessPaymentView.as_view(), name='hr-process-payment'),
]
