from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'movements'

router = DefaultRouter()
router.register('', views.MovementViewSet, basename='movements')

urlpatterns = [
    path('', include(router.urls)),
]
