from django.urls import path
from . import views

app_name = 'movements'

urlpatterns = [
    path('', views.MovementListView.as_view(), name='list_movements'),
    path('recent/', views.MovementRecentView.as_view(), name='recent_movements'),
    path('statistics/', views.MovementStatisticsView.as_view(), name='movement_statistics'),
]
