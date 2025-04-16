"""Profile URLs"""
from django.urls import path
from .views import (
    ProfileListView,
    ProfileDetailView,
    ProfileCreateView,
    ProfileUpdateView,
    ProfileDeleteView,
    ProfileAvatarView
)

app_name = 'profiles'

urlpatterns = [
    path('', ProfileListView.as_view(), name='profile-list'),
    path('<uuid:pk>/', ProfileDetailView.as_view(), name='profile-detail'),
    path('create/', ProfileCreateView.as_view(), name='profile-create'),
    path('<uuid:pk>/update/', ProfileUpdateView.as_view(), name='profile-update'),
    path('<uuid:pk>/delete/', ProfileDeleteView.as_view(), name='profile-delete'),
    path('<uuid:pk>/avatar/', ProfileAvatarView.as_view(), name='profile-avatar'),
]