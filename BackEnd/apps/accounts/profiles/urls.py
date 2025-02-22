from django.urls import path
from . import views

app_name = 'profiles'

urlpatterns = [
    path('', views.ProfileListView.as_view(), name='list_profiles'),
    path('create/', views.ProfileCreateView.as_view(), name='create_profile'),
    path('retrieve/<uuid:pk>/', views.ProfileRetrieveView.as_view(), name='retrieve_profile'),
    path('update/<uuid:pk>/', views.ProfileUpdateView.as_view(), name='update_profile'),
    path('delete/<uuid:pk>/', views.ProfileDestroyView.as_view(), name='delete_profile'),
    path('avatar/<uuid:pk>/', views.ProfileAvatarUpdateView.as_view(), name='update_avatar'),
]