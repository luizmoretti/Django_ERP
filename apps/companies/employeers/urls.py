from . import views
from django.urls import path

urlpatterns = [
    path('', views.EmployeerListView.as_view(), name='list_employeers'),
    path('create/', views.EmployeerCreateView.as_view(), name='create_employeer'),
    path('retrieve/<uuid:id>/', views.EmployeerRetrieveView.as_view(), name='retrieve_employeer'),
    path('update/<uuid:id>/', views.EmployeerUpdateView.as_view(), name='update_employeer'),
    path('delete/<uuid:id>/', views.EmployeerDestroyView.as_view(), name='delete_employeer'), 
    # path('soft-delete/<uuid:id>/', views.EmployeerSoftDeleteView.as_view(), name='soft_delete_employeer'),
]