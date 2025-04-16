from django.urls import path
from .views import BrandListView, BrandRetrieveView, BrandUpdateView, BrandDeleteView, BrandCreateView

app_name = 'brand'

urlpatterns = [
    path('', BrandListView.as_view(), name='list_brands'),
    path('create/', BrandCreateView.as_view(), name='create_brand'),
    path('retrieve/<uuid:pk>/', BrandRetrieveView.as_view(), name='retrieve_brand'),
    path('update/<uuid:pk>/', BrandUpdateView.as_view(), name='update_brand'),
    path('delete/<uuid:pk>/', BrandDeleteView.as_view(), name='delete_brand'),
]
