from . import views
from django.urls import path


urlpatterns = [
    path('me/', views.CurrentUserView.as_view(), name='current_user'),
    path('create/', views.UserCreateView.as_view(), name='create_user'),
    path('retrieve/<uuid:id>/', views.UserRetrieveView.as_view(), name='retrieve_user'),
    path('update/<uuid:id>/', views.UserUpdateView.as_view(), name='update_user'),
    path('delete/<uuid:pk>/', views.UserDeleteView.as_view(), name='delete_user'),
    path('list/', views.UserListView.as_view(), name='list_users'),
]