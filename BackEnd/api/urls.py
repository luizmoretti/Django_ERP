from django.urls import path, include
from . import views
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)


urlpatterns = [
    # Authentication endpoints
    path('token/', views.DecoratedTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', views.DecoratedTokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', views.DecoratedTokenVerifyView.as_view(), name='token_verify'),

    # Notifications endpoints
    path('notifications/', include('apps.notifications.urls')),
    
    # Swagger documentation
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # User endpoints
    path('user/', include('apps.accounts.urls')),
    path('profiles/', include('apps.accounts.profiles.urls')),
    
    # Companies endpoints
    path('companies/', include('apps.companies.urls', namespace='companies')),
    
    # Customer endpoints
    path('customers/', include('apps.companies.customers.urls')),
    
    # Employeer endpoints
    path('employeers/', include('apps.companies.employeers.urls')),
    
    # Attendance endpoints
    path('attendance/', include('apps.companies.attendance.urls')),
    
    # Delivery and Vehicle Endpoints
    path('delivery/', include('apps.delivery.urls')),
    path('vehicle/', include('apps.vehicle.urls')),
    
    # Inventory Management endpoints
    path('suppliers/', include('apps.inventory.supplier.urls')),
    path('brands/', include('apps.inventory.brand.urls')),
    path('products/', include('apps.inventory.product.urls')),
    path('transfers/', include('apps.inventory.transfer.urls')),
    path('inflows/', include('apps.inventory.inflows.urls')),
    path('outflows/', include('apps.inventory.outflows.urls')),
    path('warehouse/', include('apps.inventory.warehouse.urls')),
    path('movements/', include('apps.inventory.movements.urls')),
    path('load-orders/', include('apps.inventory.load_order.urls')),
    path('purchase-orders/', include('apps.inventory.purchase_order.urls')),
    
    
    #Scheduller endpoints
    path('scheduller/', include('apps.scheduller.urls')),
]
