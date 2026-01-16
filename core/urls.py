from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HealthViewSet

router = DefaultRouter()
router.register(r'health', HealthViewSet, basename='health')

urlpatterns = [
    path('', include(router.urls)),
]
