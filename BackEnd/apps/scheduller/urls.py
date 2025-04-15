from .views import JobsTypeSchedullerRegisterViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'jobs-type-scheduller-register', JobsTypeSchedullerRegisterViewSet)

urlpatterns = [
    
] + router.urls

