from django.urls import path, re_path
from apps.companies.customers import views

app_name = 'customers'

urlpatterns = [
    path('', views.CustomerListView.as_view(), name='list_customers'),
    path('create/', views.CustomerCreateView.as_view(), name='create_customer'),
    re_path(r'^retrieve/(?P<pk>[0-9a-f-]{36})/$', views.CustomerRetrieveByIdView.as_view(), name='retrieve_customer_by_id'),
    path('retrieve/', views.CustomerRetrieveByNameView.as_view(), name='retrieve_customer_by_name'),
    path('update/<uuid:pk>/', views.CustomerUpdateView.as_view(), name='update_customer'),
    path('delete/<uuid:pk>/', views.CustomerDeleteView.as_view(), name='delete_customer'),
    
    # Leads
    path('generate-leads/', views.GenerateLeadsView.as_view(), name='generate_customer_leads'),
    path('list-leads/', views.ListLeadsView.as_view(), name='list_customer_leads'),
]