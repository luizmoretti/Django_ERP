from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    LoginView, CustomPasswordResetView, UserListView,
    UserCreateView, UserRetrieveView, UserUpdateView,
    UserDeleteView, CurrentUserView, PasswordResetConfirmView,
    PasswordResetCompleteView
)


urlpatterns = [
    # Interface Web - Autenticação
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # Password Reset Flow
    path('password-reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('reset/<str:uidb64>/<str:token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    
    
    # API Endpoints
    path('', UserListView.as_view(), name='list_users'),
    path('create/', UserCreateView.as_view(), name='create_user'),
    path('retrieve/<uuid:pk>/', UserRetrieveView.as_view(), name='retrieve_user'),
    path('update/<uuid:pk>/', UserUpdateView.as_view(), name='update_user'),
    path('delete/<uuid:pk>/', UserDeleteView.as_view(), name='delete_user'),
    path('me/', CurrentUserView.as_view(), name='current_user'),
]