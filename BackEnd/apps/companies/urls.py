from django.urls import path

from .views import (
    CompanieListView,
    CompanieCreateView
)

app_name = 'companies'

urlpatterns = [
    # Companies endpoints
    path('', CompanieListView.as_view(), name='company-list'),
    path('create/', CompanieCreateView.as_view(), name='company-create'),
]