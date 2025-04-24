from django.urls import path
from .views import (
    JobsTypeSchedullerRegisterListView,
    JobsTypeSchedullerRegisterCreateView,
    JobsTypeSchedullerRegisterRetrieveView,
    JobsTypeSchedullerRegisterUpdateView,
    JobsTypeSchedullerRegisterDestroyView
)

urlpatterns = [
    # JobsTypeSchedullerRegister endpoints
    path('', JobsTypeSchedullerRegisterListView.as_view(), name='jobs-type-scheduller-register-list'),
    path('jobs-type-scheduller-register/create', JobsTypeSchedullerRegisterCreateView.as_view(), name='jobs-type-scheduller-register-create'),
    path('jobs-type-scheduller-register/<uuid:pk>/', JobsTypeSchedullerRegisterRetrieveView.as_view(), name='jobs-type-scheduller-register-detail'),
    path('jobs-type-scheduller-register/<uuid:pk>/', JobsTypeSchedullerRegisterUpdateView.as_view(), name='jobs-type-scheduller-register-update'),
    path('jobs-type-scheduller-register/<uuid:pk>/', JobsTypeSchedullerRegisterDestroyView.as_view(), name='jobs-type-scheduller-register-delete'),
]
