from . import views
from django.urls import path

urlpatterns = [
    path('', views.AttendanceRegisterListView.as_view(), name='list_attendance_registers'),
    path('create/', views.AttendanceRegisterCreateView.as_view(), name='create_attendance_register'),
    path('retrieve/<uuid:pk>/', views.AttendanceRegisterRetrieveView.as_view(), name='retrieve_attendance_register'),
    path('update/<uuid:pk>/', views.AttendanceRegisterUpdateView.as_view(), name='update_attendance_register'),
    path('delete/<uuid:pk>/', views.AttendanceRegisterDestroyView.as_view(), name='delete_attendance_register'),
]